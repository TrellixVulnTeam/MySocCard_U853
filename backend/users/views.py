from datetime import datetime
import json
import os
import pprint

import requests
from django.contrib import messages

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from django.urls import reverse
from purchase.utils import paginateObjects
from .forms import MolliePaymentsForm

from .models import Holder, MolliePayments, Personel, WalletUpgrades
from core.settings import mollie_client

# Create your views here.


def safe_json_decode(
    response,
):
    if response.status_code == 500:
        raise Exception("500")
    # elif response.status_code == 400:
    #     raise Exception("400")
    # elif response.status_code == 401:
    #     raise Exception("401")
    else:
        try:
            return (
                response,
                response.json(),
            )
        except json.decoder.JSONDecodeError:
            raise Exception(
                "500",
                "Ledenbase response not readable or empty",
            )


@login_required(login_url="login")
def showUsers(request):
    users = Holder.objects.all()
    return render(request)


@login_required(login_url="login")
def home(request):
    user = Holder.objects.get(user=request.user)
    purchases = user.purchases.all()
    custom_range, purchases = paginateObjects(request, list(purchases), 10, "purchase_page")
    content = {
        "user": user,
        "purchases": purchases,
        "custom_range": custom_range,
    }
    return render(request, "users/home.html", content)


def loginLedenbase(request):
    LEDENBASE_TOKEN = os.environ.get("LEDENBASE_TOKEN")
    LEDENBASE_URL = os.environ.get("LEDENBASE_URL")
    login_res = requests.post(
        f"{LEDENBASE_URL}/login/",
        headers={"Content-Type": "application/json", "Accept": "application/json", "Authorization": LEDENBASE_TOKEN},
        json={
            "password": request.POST.get("password"),
            "username": request.POST.get("username"),
        },
    )
    lid_token = login_res.text
    if login_res.status_code != 200:
        try:

            messages.error(
                request,
                "Error 4032:" + lid_token["non_field_errors"][0],
            )
        except:
            messages.error(
                request,
                "Error 4041: No response from Ledenbase",
            )
        return None
    if login_res.status_code == 200:
        person_res = requests.get(
            f"{LEDENBASE_URL}/personen/{json.loads(lid_token).get('token')}/",
            headers={"Content-Type": "application/json", "Accept": "application/json", "Authorization": LEDENBASE_TOKEN},
        )
        ledenbase_lid = json.loads(person_res.text)
        (user, created,) = User.objects.get_or_create(
            username=request.POST.get("username"),
            # user purposely doesnt have a password set here to make sure it
        )
        user.first_name = ledenbase_lid.get("voornaam")
        user.last_name = ledenbase_lid.get("achternaam")
        user.is_superuser = ledenbase_lid.get("is_administrator")
        if not user.is_staff and ledenbase_lid.get("is_administrator"):
            user.is_staff = True

        user.save()
        (holder, created,) = Holder.objects.get_or_create(
            user=user,
        )
        holder.ledenbase_id = ledenbase_lid.get("id")
        holder.image_ledenbase = ledenbase_lid.get("foto")
        holder.save()
        if created:
            messages.info(
                request,
                "User and Holder were created",
            )
        return user


def loginUser(request):
    if request.user.is_authenticated:
        return redirect("userHome")
    if request.method == "POST":
        user1 = User.objects.filter(username=request.POST["username"])
        if user1.exists() and user1.filter(holder__ledenbase_id=0).exists():
            # print("user exists and doesnt have ledenbase id")
            user = authenticate(
                password=request.POST["password"],
                username=request.POST["username"],
            )
        else:
            user = loginLedenbase(request)
        if user:
            login(
                request,
                user,
            )
            messages.info(
                request,
                "User was logged in",
            )
            return redirect(request.GET["next"] if "next" in request.GET else "userHome")
        else:
            messages.error(
                request,
                "Username or password is incorrect",
            )

    return render(
        request,
        "users/login.html",
    )


def logoutUser(request):
    logout(request)
    messages.info(
        request,
        "User logged out",
    )
    return redirect("login")


@login_required(login_url="login")
def app(request):
    return render(
        request,
        "users/app.html",
    )


@login_required(login_url="login")
def mollieReturn(request, *args, **kwargs):
    molliePayment = MolliePayments.objects.get(identifier=kwargs["identifier"])
    print(
        "molliePayment",
        {"molliePayment.id": molliePayment.id, "molliePayment.payment_id": molliePayment.payment_id, "molliePayment.identifier": molliePayment.identifier},
    )
    payment = mollie_client.payments.get(molliePayment.payment_id)
    if payment.status == "paid":
        messages.info(
            request,
            f"Betaling is gelukt, je hebt nu {payment.amount['value']} {payment.amount['currency']} op je account",
        )
        molliePayment.is_paid = True
        molliePayment.payed_on = datetime.now()
        molliePayment.save()
        WalletUpgrades.objects.create(
            holder=molliePayment.holder,
            amount=float(molliePayment.amount),
            comment=f"Upgrade via mollie payment {molliePayment.payment_id}",
            seller=Personel.objects.get(id=5),
            molliePayment=molliePayment,
        )
    else:
        messages.error(
            request,
            "Payment was not succesful",
        )
    return redirect("userHome")


@login_required(login_url="login")
@csrf_exempt
def mollieWebhook(request, *args, **kwargs):
    molliePayment = MolliePayments.objects.get(identifier=kwargs["identifier"])
    payment = mollie_client.payments.get(molliePayment.payment_id)
    if payment.status == "paid":
        molliePayment.is_paid = True
        molliePayment.payed_on = datetime.now()
        molliePayment.save()
        WalletUpgrades.objects.create(
            holder=molliePayment.holder,
            amount=float(molliePayment.amount),
            comment=f"Upgrade via mollie payment {molliePayment.payment_id}",
            seller=Personel.objects.get(id=5),
            molliePayment=molliePayment,
        )
    else:
        messages.error(
            request,
            "Payment was not succesful",
        )
    return redirect("userHome")


@login_required(login_url="login")
def paymentUpgrade(request):
    form = MolliePaymentsForm()
    if request.method == "POST":
        form = MolliePaymentsForm(request.POST)
        if form.is_valid():
            molliePayment = form.save(commit=False)
            molliePayment.holder = request.user.holder
            body = {
                "amount": {"currency": "EUR", "value": f"{molliePayment.amount:.2f}"},
                "description": f"Mamon | Wallet Opwarderen  €{molliePayment.amount:.2f}",
                "redirectUrl": request.build_absolute_uri(reverse("mollie-return", args=[str(molliePayment.identifier)])),
                "webhookUrl": request.build_absolute_uri(reverse("mollie-webhook", args=[str(molliePayment.identifier)])),
                "method": ["applepay", "creditcard", "ideal"],
                "metadata": {"identifier": str(molliePayment.identifier)},
            }
            payment = mollie_client.payments.create(body)
            molliePayment.payment_id = payment.id
            molliePayment.expiry_date = payment.get("expiresAt")
            molliePayment.save()
            return redirect(payment.checkout_url)
    content = {
        "form": form,
    }
    return render(request, "users/paymentUpgrade.html", content)
