import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, UpdateDateColumn, ManyToOne, OneToMany, JoinColumn } from "typeorm";
import { User } from "./User";
import { Family } from "./Family";
import { Product } from "./Product";

export enum OrderStatus {
    PENDING = "PENDING",
    ACCEPTED = "ACCEPTED",
    PREPARING = "PREPARING",
    READY_FOR_PICKUP = "READY_FOR_PICKUP",
    ON_WAY = "ON_WAY",
    DELIVERED = "DELIVERED",
    CANCELLED = "CANCELLED",
    REJECTED = "REJECTED"
}

@Entity("orders")
export class Order {
    @PrimaryGeneratedColumn()
    id!: number;

    @Column("decimal", { precision: 10, scale: 2 })
    total_amount!: number;

    @Column("decimal", { precision: 10, scale: 2 })
    delivery_fee!: number;

    @Column({
        type: "text",
        default: OrderStatus.PENDING
    })
    status!: OrderStatus;

    @Column({ nullable: true })
    delivery_address!: string;

    @Column("text", { nullable: true })
    notes!: string;

    @ManyToOne(() => User)
    @JoinColumn({ name: "buyer_id" })
    buyer!: User;

    @Column({ nullable: true })
    buyer_id!: number;

    @ManyToOne(() => Family)
    @JoinColumn({ name: "family_id" })
    family!: Family;

    @Column({ nullable: true })
    family_id!: number;

    @OneToMany(() => OrderItem, (item) => item.order)
    items!: OrderItem[];

    @CreateDateColumn()
    created_at!: Date;

    @UpdateDateColumn()
    updated_at!: Date;
}

@Entity("order_items")
export class OrderItem {
    @PrimaryGeneratedColumn()
    id!: number;

    @ManyToOne(() => Order, (order) => order.items)
    @JoinColumn({ name: "order_id" })
    order!: Order;

    @Column()
    order_id!: number;

    @ManyToOne(() => Product)
    @JoinColumn({ name: "product_id" })
    product!: Product;

    @Column({ nullable: true })
    product_id!: number;

    @Column()
    quantity!: number;

    @Column("decimal", { precision: 10, scale: 2 })
    unit_price!: number;

    @Column("decimal", { precision: 10, scale: 2 })
    total_price!: number;
}
