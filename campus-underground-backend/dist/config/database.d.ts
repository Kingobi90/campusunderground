import { Pool } from 'pg';
export declare const config: {
    host: string;
    port: number;
    database: string;
    user: string;
    password: string;
    ssl: boolean | {
        rejectUnauthorized: boolean;
    };
};
export declare const pool: Pool;
export default pool;
//# sourceMappingURL=database.d.ts.map