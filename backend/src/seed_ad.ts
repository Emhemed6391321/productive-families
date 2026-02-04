import { AppDataSource } from "../data-source";
import { User } from "../entities/User";
import { Family } from "../entities/Family";
import { FeaturedAd } from "../entities/FeaturedAd";

async function seed() {
    try {
        await AppDataSource.initialize();
        console.log("Database connected.");

        const userRepository = AppDataSource.getRepository(User);
        const familyRepository = AppDataSource.getRepository(Family);
        const adRepository = AppDataSource.getRepository(FeaturedAd);

        // 1. Get or Create User
        let user = await userRepository.findOneBy({ email: "demo_family@test.com" });
        if (!user) {
            user = new User();
            user.full_name = "Demo Family Owner";
            user.email = "demo_family@test.com";
            user.password_hash = "password123"; // In real app should be hashed
            user.phone_number = "0555555555";
            user.role = "family";
            await userRepository.save(user);
            console.log("Created Demo User");
        }

        // 2. Get or Create Family
        let family = await familyRepository.findOneBy({ user_id: user.id });
        if (!family) {
            family = new Family();
            family.user = user;
            family.business_name = "مطبخ السعادة";
            family.description = "أشهى المأكولات المنزلية والحلويات الشرقية بأيدي خبيرة.";
            family.min_order_amount = 50;
            family.delivery_fee = 15;
            family.rating = 4.8;
            family.review_count = 120;
            await familyRepository.save(family);
            console.log("Created Demo Family");
        }

        // 3. Create Featured Ad
        const ad = new FeaturedAd();
        ad.family = family;
        ad.start_date = new Date();
        const endDate = new Date();
        endDate.setDate(endDate.getDate() + 7); // Active for 7 days
        ad.end_date = endDate;
        ad.price_paid = 100;
        ad.active = true;

        await adRepository.save(ad);
        console.log("Created Featured Ad for 'مطبخ السعادة'");

    } catch (error) {
        console.error("Error seeding:", error);
    } finally {
        await AppDataSource.destroy();
    }
}

seed();
