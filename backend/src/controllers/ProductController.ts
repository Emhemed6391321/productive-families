import { Request, Response } from "express";
import { AppDataSource } from "../data-source";
import { Product } from "../entities/Product";
import { Family } from "../entities/Family";

const productRepository = AppDataSource.getRepository(Product);
const familyRepository = AppDataSource.getRepository(Family);

export class ProductController {
    // Add new product
    // Arabic: إضافة منتج جديد
    static async create(req: Request, res: Response) {
        try {
            const { family_id, name, description, price, preparation_time_minutes } = req.body;

            const family = await familyRepository.findOneBy({ id: family_id });
            if (!family) {
                return res.status(404).json({ message: "Family not found" });
            }

            const product = new Product();
            product.family = family;
            product.name = name;
            product.description = description;
            product.price = price;
            product.preparation_time_minutes = preparation_time_minutes;

            await productRepository.save(product);

            return res.status(201).json({ message: "Product created", product });
        } catch (error) {
            console.error(error);
            return res.status(500).json({ message: "Error creating product" });
        }
    }

    // Get products by family
    // Arabic: عرض منتجات أسرة معينة
    static async getByFamily(req: Request, res: Response) {
        try {
            const { familyId } = req.params;
            const parsedFamilyId = typeof familyId === 'string' ? parseInt(familyId) : parseInt(familyId[0]);

            const products = await productRepository.find({
                where: { family_id: parsedFamilyId },
                relations: ['family']
            });
            return res.status(200).json(products);
        } catch (error) {
            return res.status(500).json({ message: "Error fetching products" });
        }
    }

    // Get all products (Public/Admin)
    // Arabic: عرض جميع المنتجات
    static async getAll(req: Request, res: Response) {
        try {
            const products = await productRepository.find({
                relations: ['family'],
                order: { created_at: 'DESC' }
            });
            return res.status(200).json(products);
        } catch (error) {
            console.error(error);
            return res.status(500).json({ message: "Error fetching all products" });
        }
    }
    // Update product
    static async update(req: Request, res: Response) {
        try {
            const { id } = req.params;
            const productId = typeof id === 'string' ? parseInt(id) : parseInt(id[0]);
            const { name, description, price, preparation_time_minutes } = req.body;

            const product = await productRepository.findOneBy({ id: productId });
            if (!product) {
                return res.status(404).json({ message: "Product not found" });
            }

            product.name = name || product.name;
            product.description = description || product.description;
            product.price = price || product.price;
            product.preparation_time_minutes = preparation_time_minutes || product.preparation_time_minutes;

            await productRepository.save(product);
            return res.status(200).json({ message: "Product updated", product });
        } catch (error) {
            console.error(error);
            return res.status(500).json({ message: "Error updating product" });
        }
    }

    // Delete product
    static async delete(req: Request, res: Response) {
        try {
            const { id } = req.params;
            const result = await productRepository.delete(id);

            if (result.affected === 0) {
                return res.status(404).json({ message: "Product not found" });
            }

            return res.status(200).json({ message: "Product deleted successfully" });
        } catch (error) {
            console.error(error);
            return res.status(500).json({ message: "Error deleting product" });
        }
    }
}
