import { ErrorType } from ".";

export default class GenericException extends Error {
  type: ErrorType;
  router?: string;
  constructor(
    message: string = "Ocorreu um erro inesperado!",
    type: ErrorType = "error",
  ) {
    super(message);
    this.name = "Error Generic Exception";
    this.type = type;
    this.message = message;
  }
}
