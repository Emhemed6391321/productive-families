import { Request, Response } from "express";
import { AppDataSource } from "../data-source";
import { User } from "../entities/User";

const userRepository = AppDataSource.getRepository(User);

export class UserController {
    // Register a new user
    static async register(req: Request, res: Response) {
        try {
            const { full_name, email, password, phone_number, role } = req.body;

            // Check if user exists
            const existingUser = await userRepository.findOne({
                where: [{ email }, { phone_number }]
            });

            if (existingUser) {
                return res.status(400).json({ message: "User already exists with this email or phone number." });
            }

            // Create new user
            const user = new User();
            user.full_name = full_name;
            user.email = email;
            user.phone_number = phone_number;
            user.role = role || "BUYER";
            user.password_hash = password; // In real app, hash this password!

            await userRepository.save(user);

            return res.status(201).json({ message: "User created successfully", user });
        } catch (error) {
            console.error(error);
            return res.status(500).json({ message: "Error registering user" });
        }
    }

    // Login user
    static async login(req: Request, res: Response) {
        try {
            const { email, password } = req.body;

            const user = await userRepository.findOne({ where: { email } });

            if (!user) {
                return res.status(404).json({ message: "User not found" });
            }

            // In real app, verify hash. Here simple check
            if (user.password_hash !== password) {
                return res.status(401).json({ message: "Invalid credentials" });
            }

            return res.status(200).json({ message: "Login successful", user });
        } catch (error) {
            return res.status(500).json({ message: "Error logging in" });
        }
    }

    // Get all users
    static async getAll(req: Request, res: Response) {
        try {
            const users = await userRepository.find();
            return res.status(200).json(users);
        } catch (error) {
            return res.status(500).json({ message: "Error fetching users" });
        }
    }
}
