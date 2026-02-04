import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, ManyToOne, JoinColumn } from "typeorm";
import { Family } from "./Family";

@Entity("products")
export class Product {
    @PrimaryGeneratedColumn()
    id!: number;

    @Column()
    name!: string;

    @Column("text", { nullable: true })
    description!: string;

    @Column("decimal", { precision: 10, scale: 2 })
    price!: number;

    @Column("decimal", { precision: 10, scale: 2, nullable: true })
    discount_price!: number;

    @Column({ nullable: true })
    image_url!: string;

    @Column({ default: true })
    is_available!: boolean;

    @Column({ nullable: true })
    preparation_time_minutes!: number;

    @ManyToOne(() => Family)
    @JoinColumn({ name: "family_id" })
    family!: Family;

    @Column()
    family_id!: number;

    @CreateDateColumn()
    created_at!: Date;
}
