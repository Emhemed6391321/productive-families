import { Request, Response } from "express";
import { AppDataSource } from "../data-source";
import { Family } from "../entities/Family";
import { User, UserRole } from "../entities/User";

const familyRepository = AppDataSource.getRepository(Family);
const userRepository = AppDataSource.getRepository(User);

export class FamilyController {
    // Register a family profile (Become a seller)
    // Arabic: تسجيل أسرة منتجة جديدة
    static async create(req: Request, res: Response) {
        try {
            const { user_id, business_name, description, min_order_amount, delivery_fee } = req.body;

            const user = await userRepository.findOneBy({ id: user_id });
            if (!user) {
                return res.status(404).json({ message: "User not found" });
            }

            // Check if user already has a family profile
            const existingFamily = await familyRepository.findOneBy({ user_id });
            if (existingFamily) {
                return res.status(400).json({ message: "User already has a family profile" });
            }

            const family = new Family();
            family.user = user;
            family.business_name = business_name;
            family.description = description;
            family.min_order_amount = min_order_amount || 0;
            family.delivery_fee = delivery_fee || 0;

            await familyRepository.save(family);

            // Update user role to FAMILY_OWNER
            user.role = UserRole.FAMILY_OWNER;
            await userRepository.save(user);

            return res.status(201).json({ message: "Family profile created", family });
        } catch (error) {
            console.error(error);
            return res.status(500).json({ message: "Error creating family profile" });
        }
    }

    // Get all families (for buyers to browse)
    // Arabic: عرض كل الأسر المنتجة
    static async getAll(req: Request, res: Response) {
        try {
            const families = await familyRepository.find();
            return res.status(200).json(families);
        } catch (error) {
            return res.status(500).json({ message: "Error fetching families" });
        }
    }
}
