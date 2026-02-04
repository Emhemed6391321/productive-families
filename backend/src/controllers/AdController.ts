import { Request, Response } from "express";
import { AppDataSource } from "../data-source";
import { FeaturedAd } from "../entities/FeaturedAd";
import { Family } from "../entities/Family";
import { LessThanOrEqual, MoreThanOrEqual } from "typeorm";

const adRepository = AppDataSource.getRepository(FeaturedAd);
const familyRepository = AppDataSource.getRepository(Family);

export class AdController {
    // Create a new featured ad (Admin only)
    static async create(req: Request, res: Response) {
        try {
            const { family_id, duration_days, price_paid } = req.body;

            const family = await familyRepository.findOneBy({ id: family_id });
            if (!family) {
                return res.status(404).json({ message: "Family not found" });
            }

            const startDate = new Date();
            const endDate = new Date();
            endDate.setDate(startDate.getDate() + (duration_days || 7)); // Default 7 days

            const ad = new FeaturedAd();
            ad.family = family;
            ad.start_date = startDate;
            ad.end_date = endDate;
            ad.price_paid = price_paid || 0;
            ad.active = true;

            await adRepository.save(ad);

            return res.status(201).json({ message: "Promotional ad created", ad });
        } catch (error) {
            console.error(error);
            return res.status(500).json({ message: "Error creating ad" });
        }
    }

    // Get active ads (Public)
    static async getActive(req: Request, res: Response) {
        try {
            const currentDate = new Date();

            const ads = await adRepository.find({
                where: {
                    active: true,
                    // start_date <= current <= end_date logic is bit complex in simple find, 
                    // simplifying for now to just checking active flag and maybe client side filter or explicit query builder
                    // For MVP let's assume active flag is managed or we allow fetching all active marked ones
                },
                relations: ['family'],
                order: { created_at: 'DESC' }
            });

            // Filter by date manually for simplicity in TypeORM simple find
            const validAds = ads.filter(ad =>
                new Date(ad.start_date) <= currentDate &&
                new Date(ad.end_date) >= currentDate
            );

            return res.status(200).json(validAds);
        } catch (error) {
            console.error(error);
            return res.status(500).json({ message: "Error fetching ads" });
        }
    }
}
