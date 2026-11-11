import client from './client'

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
  role: string
  user_id: string
}

export interface CurrentUserResponse {
  user_id: string
  role: 'student' | 'teacher' | 'admin'
  tenant_id: string
  user_name?: string
  username?: string
}

export const authApi = {
  login: (data: LoginRequest) =>
    client.post<LoginResponse>('/auth/login', data),

  me: () =>
    client.get<CurrentUserResponse>('/auth/me'),
}
