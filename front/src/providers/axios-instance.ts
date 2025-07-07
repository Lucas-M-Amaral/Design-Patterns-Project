import env from "@/config/env";
import axios from "axios";
interface AxiosInstanceProps {
  getToken?: () => Promise<string>;
}
const AxiosInstance = ({ getToken }: AxiosInstanceProps) => {
  const provider = axios.create({
    baseURL: env.BACKEND_API_URL,
  });

  try {
    if (getToken) {
      provider.interceptors.request.use(async (config) => {
        const token = await getToken();
        config.headers.Authorization = `Bearer ${token}`;
        return config;
      });
    }
  } catch (error) {}

  return {
    provider,
  };
};

export default AxiosInstance;
