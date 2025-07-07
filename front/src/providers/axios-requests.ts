import ApiException from "@/exceptions/api";
import GenericException from "@/exceptions/generic";
import axios, { AxiosInstance, AxiosRequestConfig } from "axios";

export const ProviderRequest = (provider: AxiosInstance) => {
  const get = async <T>(
    path: string,
    options?: AxiosRequestConfig,
  ): Promise<T> => {
    try {
      const response = await provider.get<T>(path, options);

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new ApiException(
          error.response?.data?.title,
          "error",
          error.response?.status,
        );
      }
      throw new GenericException();
    }
  };

  const post = async <D, R>(
    path: string,
    data?: D,
    options?: AxiosRequestConfig,
  ): Promise<R> => {
    try {
      const response = await provider.post<R>(path, data, options);

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.status !== 500) {
        throw new ApiException(
          error.response?.data?.title,
          "error",
          error.response?.status,
        );
      }
      throw new GenericException();
    }
  };

  const put = async <D, R>(
    path: string,
    data?: D,
    options?: AxiosRequestConfig,
  ): Promise<R> => {
    try {
      const response = await provider.put<R>(path, data, options);

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.status !== 500) {
        throw new ApiException(
          error.response?.data?.title,
          "error",
          error.response?.status,
        );
      }
      throw new GenericException();
    }
  };

  const deleted = async <R>(
    path: string,
    options?: AxiosRequestConfig,
  ): Promise<R> => {
    try {
      const response = await provider.delete<R>(path, options);

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.status !== 500) {
        throw new ApiException(
          error.response?.data?.title,
          "error",
          error.response?.status,
        );
      }
      throw new GenericException();
    }
  };

  const patch = async <D, R>(
    path: string,
    data?: D,
    options?: AxiosRequestConfig,
  ): Promise<R> => {
    try {
      const response = await provider.patch<R>(path, data, options);

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.status !== 500) {
        throw new ApiException(
          error.response?.data?.title,
          "error",
          error.response?.status,
        );
      }
      throw new GenericException();
    }
  };

  return {
    get,
    post,
    put,
    deleted,
    patch,
  };
};
