import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, ManyToOne, JoinColumn } from "typeorm";
import { Family } from "./Family";

@Entity("featured_ads")
export class FeaturedAd {
    @PrimaryGeneratedColumn()
    id!: number;

    @ManyToOne(() => Family)
    @JoinColumn({ name: "family_id" })
    family!: Family;

    @Column()
    family_id!: number;

    @Column("datetime")
    start_date!: Date;

    @Column("datetime")
    end_date!: Date;

    @Column({ default: true })
    active!: boolean;

    @Column("decimal", { precision: 10, scale: 2 })
    price_paid!: number;

    @CreateDateColumn()
    created_at!: Date;
}
