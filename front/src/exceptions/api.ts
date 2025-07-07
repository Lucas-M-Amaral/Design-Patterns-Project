import { ErrorType } from ".";
import GenericException from "./generic";

export default class ApiException extends GenericException {
  status: number;
  constructor(
    message = "Ocorreu um erro com a comunicação da api",
    type: ErrorType = "error",
    status: number = 500,
  ) {
    super(message, type);
    this.status = status;
  }
}

export type BuildedException = {
  title: string;
  status: number;
};
export function isBuildedApiException(obj: unknown): obj is BuildedException {
  return (
    (obj as BuildedException)?.title !== undefined &&
    typeof (obj as BuildedException).title === "string"
  );
}
