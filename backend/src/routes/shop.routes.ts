import { Router } from "express";
import { FamilyController } from "../controllers/FamilyController";
import { ProductController } from "../controllers/ProductController";

const router = Router();

// Family Routes
router.post("/families", FamilyController.create);
router.get("/families", FamilyController.getAll);

// Product Routes
router.post("/products", ProductController.create);
router.get("/products", ProductController.getAll);
router.get("/products/family/:familyId", ProductController.getByFamily);
router.put("/products/:id", ProductController.update);
router.delete("/products/:id", ProductController.delete);

// Ad Routes
import { AdController } from "../controllers/AdController";
router.post("/ads", AdController.create);
router.get("/ads", AdController.getActive);

export default router;
