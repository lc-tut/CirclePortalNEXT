/**
 * Type definitions for API models
 */

export type Campus = "八王子" | "蒲田";
export type CircleCategory = "運動系" | "文化系" | "委員会";
export type CircleRole = "Leader" | "Member";
export type SysRole = "SystemAdmin" | "General";
export type ViewType = "public" | "internal";

export interface User {
    id: string;
    username: string;
    email: string;
    sys_role: SysRole;
    auth_user_id?: string;
    created_at: string;
}

export interface Circle {
    id: string;
    name: string;
    campus: Campus;
    category: CircleCategory;
    description: string;
    location?: string;
    activity_detail?: string;
    logo_url?: string;
    cover_image_url?: string;
    is_published: boolean;
    created_at: string;
    updated_at: string;
    deleted_at?: string;
}

export interface CircleDetail extends Circle {
    view_type: ViewType;
}

export interface Event {
    id: string;
    circle_id: string;
    title: string;
    event_date_start: string;
    event_date_end: string;
    place: string;
    description: string;
    deleted_at?: string;
}
