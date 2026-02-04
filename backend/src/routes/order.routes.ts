import { Router } from "express";
import { OrderController } from "../controllers/OrderController";

const router = Router();

router.post("/", OrderController.create);
router.get("/family/:familyId", OrderController.getFamilyOrders);

export default router;
