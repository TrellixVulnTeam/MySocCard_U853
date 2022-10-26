import { createContext, useContext, useState } from "react";

import AuthContext from "./AuthContext.tsx";
import PurchaseContext from "./PurchaseContext";
import { number } from "prop-types";

/**cart: cart,
 * 
 * setCart: setCart, 
 * 
    add_to_cart: add_to_cart,

    remove_from_cart: remove_from_cart,

    buy_cart: buy_cart,
     */
const CartContext = createContext({
  cart: [],
  buyer: number,
  setBuyer: () => {},
  setCart: () => {},
  add_to_cart: (product) => {},
  remove_from_cart: (product, quantity = 1) => {},
  buy_cart: async (buy, sell) => {},
});
export default CartContext;

export const CartProvider = ({ children }) => {
  const { POST } = useContext(PurchaseContext);
  const { user } = useContext(AuthContext);
  /**withing a cart there are orders
   * orders consist of an object in the following form
   * {quantity: int,
   *  product: product.id<int>}
   * when adding or removing from the cart you are
   * looking up the oder by product key and then ajusting the quantity 
   * if the quantity is 0 then you can remove the order from the cart
   */

  const [buyer, setBuyer] = useState(null);
  const [cart, setCart] = useState([]);
  function add_to_cart(product) {
    cart.some((order) => order.product === product.id)
      ? setCart(() =>
          cart.map((order) =>
            order.product === product.id
              ? { ...order, quantity: order.quantity + 1 }
              : order
          )
        )
      : setCart(() => [...cart, { quantity: 1, product: product.id }]);
  }
  function remove_from_cart(product, quantity = 1) {
    if (cart.some((order) => order.product === product.id)) {
      if (
        cart.find((order) => order.product === product.id).quantity === quantity
      ) {
        setCart(() => cart.filter((order) => order.product !== product.id));
      } else {
        cart.find((order) => order.product === product.id).quantity > 1
          ? setCart(() =>
              cart.map((order) =>
                order.product === product.id
                  ? { ...order, quantity: order.quantity - quantity }
                  : order
              )
            )
          : setCart(() => cart.filter((order) => order.product !== product.id));
      }
    }
  }
  async function buy_cart(buyer, sell) {
    await POST({
      orders: cart,
      seller: user?.holder_id ? user?.holder_id : 0,
      payed: sell === true ? true : false,
      buyer: buyer ? buyer : 0,
    });
    setCart([]);
  }

  const data = {
    cart: cart,
    setCart: setCart,
    add_to_cart: add_to_cart,
    remove_from_cart: remove_from_cart,
    buy_cart: buy_cart,
    buyer: buyer,
    setBuyer: setBuyer,
  };
  return <CartContext.Provider value={data}>{children}</CartContext.Provider>;
};