import "reflect-metadata";
import express from "express";
import cors from "cors";
import helmet from "helmet";
import dotenv from "dotenv";

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(helmet());
app.use(express.json());

// Initialize Database
import { AppDataSource } from "./data-source";
AppDataSource.initialize()
    .then(() => {
        console.log("Data Source has been initialized!");
    })
    .catch((err) => {
        console.error("Error during Data Source initialization:", err);
    });

// Routes
import userRoutes from "./routes/user.routes";
import shopRoutes from "./routes/shop.routes";
import orderRoutes from "./routes/order.routes";

app.use("/api/users", userRoutes);
app.use("/api/shop", shopRoutes);
app.use("/api/orders", orderRoutes);

// Basic Route
app.get("/", (req, res) => {
    res.send("Productive Families API is running!");
});

// Start Server
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
