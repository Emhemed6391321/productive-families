import { Request, Response } from "express";
import { AppDataSource } from "../data-source";
import { Order, OrderStatus } from "../entities/Order";
import { OrderItem } from "../entities/Order";
import { Product } from "../entities/Product";
import { User } from "../entities/User";
import { Family } from "../entities/Family";

const orderRepository = AppDataSource.getRepository(Order);
const orderItemRepository = AppDataSource.getRepository(OrderItem);
const productRepository = AppDataSource.getRepository(Product);
const userRepository = AppDataSource.getRepository(User);
const familyRepository = AppDataSource.getRepository(Family);

export class OrderController {
    // Place a new order
    // Arabic: إنشاء طلب جديد
    static async create(req: Request, res: Response) {
        try {
            const { buyer_id, family_id, items, delivery_address, notes } = req.body;
            // items: [{ product_id: 1, quantity: 2 }]

            const buyer = await userRepository.findOneBy({ id: buyer_id });
            const family = await familyRepository.findOneBy({ id: family_id });

            if (!buyer || !family) {
                return res.status(404).json({ message: "Buyer or Family not found" });
            }

            // Calculate totals and validate products
            let totalAmount = 0;
            const orderItemsEntities: OrderItem[] = [];

            for (const item of items) {
                const product = await productRepository.findOneBy({ id: item.product_id });
                if (!product) {
                    return res.status(400).json({ message: `Product ${item.product_id} not found` });
                }

                const unitPrice = product.discount_price || product.price;
                const totalPrice = unitPrice * item.quantity;

                const orderItem = new OrderItem();
                orderItem.product = product;
                orderItem.quantity = item.quantity;
                orderItem.unit_price = unitPrice;
                orderItem.total_price = totalPrice;

                orderItemsEntities.push(orderItem);
                totalAmount += totalPrice;
            }

            const order = new Order();
            order.buyer = buyer;
            order.family = family;
            order.total_amount = totalAmount;
            order.delivery_fee = family.delivery_fee;
            order.status = OrderStatus.PENDING;
            order.delivery_address = delivery_address; // In real app, simpler string or use lat/lng
            order.notes = notes;

            // Save order first
            const savedOrder = await orderRepository.save(order);

            // Save items linked to order
            for (const item of orderItemsEntities) {
                item.order = savedOrder;
                await orderItemRepository.save(item);
            }

            return res.status(201).json({ message: "Order placed successfully", order: savedOrder });

        } catch (error) {
            console.error(error);
            return res.status(500).json({ message: "Error placing order" });
        }
    }

    // Get orders for a family (Seller View)
    // Arabic: عرض الطلبات الخاصة بالأسرة
    static async getFamilyOrders(req: Request, res: Response) {
        try {
            const { familyId } = req.params;
            const parsedFamilyId = typeof familyId === 'string' ? parseInt(familyId) : parseInt(familyId[0]);

            const orders = await orderRepository.find({
                where: { family_id: parsedFamilyId },
                relations: ["buyer", "items", "items.product"],
                order: { created_at: "DESC" }
            });
            return res.status(200).json(orders);
        } catch (error) {
            return res.status(500).json({ message: "Error fetching orders" });
        }
    }
}
