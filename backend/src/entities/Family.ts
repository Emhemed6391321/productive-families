import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, OneToOne, JoinColumn } from "typeorm";
import { User } from "./User";

@Entity("families")
export class Family {
    @PrimaryGeneratedColumn()
    id!: number;

    @Column()
    business_name!: string;

    @Column("text", { nullable: true })
    description!: string;

    @Column({ nullable: true })
    logo_url!: string;

    @Column({ nullable: true })
    banner_url!: string;

    @Column({ default: false })
    is_verified!: boolean;

    @Column("decimal", { precision: 3, scale: 2, default: 0 })
    rating!: number;

    @Column({ default: 0 })
    review_count!: number;

    @Column("decimal", { precision: 10, scale: 2, default: 0 })
    min_order_amount!: number;

    @Column("decimal", { precision: 10, scale: 2, default: 0 })
    delivery_fee!: number;

    @OneToOne(() => User)
    @JoinColumn({ name: "user_id" })
    user!: User;

    @Column()
    user_id!: number;

    @CreateDateColumn()
    created_at!: Date;
}
