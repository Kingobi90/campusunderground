"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.pool = exports.config = void 0;
const pg_1 = require("pg");
const dotenv_1 = __importDefault(require("dotenv"));
dotenv_1.default.config();
exports.config = {
    host: process.env.DB_HOST || 'localhost',
    port: parseInt(process.env.DB_PORT || '5432'),
    database: process.env.DB_NAME || 'campus_underground',
    user: process.env.DB_USER || 'postgres',
    password: process.env.DB_PASSWORD || '',
    ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
};
exports.pool = new pg_1.Pool(exports.config);
// Test database connection
exports.pool.connect((err, client, release) => {
    if (err) {
        console.error('❌ Database connection failed:', err.message);
    }
    else {
        console.log('✅ Database connected successfully');
        release();
    }
});
exports.default = exports.pool;
//# sourceMappingURL=database.js.map