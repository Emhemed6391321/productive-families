import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, UpdateDateColumn, OneToMany } from "typeorm";

export enum UserRole {
    BUYER = "BUYER",
    ADMIN = "ADMIN",
    FAMILY_OWNER = "FAMILY_OWNER"
}

@Entity("users")
export class User {
    @PrimaryGeneratedColumn()
    id!: number;

    @Column()
    full_name!: string;

    @Column({ unique: true })
    email!: string;

    @Column({ unique: true, nullable: true })
    phone_number!: string;

    @Column()
    password_hash!: string;

    @Column({
        type: "text", // using 'text' compatible with postgres and others for enum simulation or simple string
        default: UserRole.BUYER
    })
    role!: UserRole;

    @Column({ nullable: true })
    profile_image_url!: string;

    @CreateDateColumn()
    created_at!: Date;

    @UpdateDateColumn()
    updated_at!: Date;
}
