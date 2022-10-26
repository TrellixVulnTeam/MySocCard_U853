import { StyleSheet, Text, View } from "react-native";

import { Card } from "@rneui/themed";
import ProductContext from "../context/ProductContext";
import { useContext } from "react";

const Purchase = ({ purchase }) => {
  const { products } = useContext(ProductContext);
  let total = 0;
  purchase?.orders?.map(
    (order) =>
      (total +=
        products?.find((productM) => productM.id === order.product)?.price *
        order.quantity)
  );
  const created = new Date(purchase?.created);
  return (
    <Card style={styles.container}>
      <Text>
        {/* {holders?.find((holder) => holder.id === purchase?.buyer).name}  */}
        For a {purchase?.payed ? "payed" : "loged"} total of €
        {parseFloat(total).toPrecision(total <= 10 ? 3 : total <= 100 ? 4 : 5)}{" "}
        on {created.toDateString()} {created.toLocaleTimeString("nl-NL")}:
      </Text>
      {purchase?.orders?.map((order) => (
        <View key={"cart product" + order.product}>
          <Text>
            {order.quantity}{" "}
            {products?.find((product) => product.id === order.product)?.name}
            {order.quantity > 1 && "s"}
          </Text>
        </View>
      ))}
    </Card>
  );
};

export default Purchase;

const styles = StyleSheet.create({ container: {} });