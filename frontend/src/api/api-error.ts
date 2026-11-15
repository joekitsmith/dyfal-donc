export class ApiError extends Error {
  readonly status: number;

  constructor(status: number) {
    super(`The server returned status ${status}`);
    this.status = status;
  }
}

/** The data of a response, or an ApiError carrying the status when the request failed. */
export function unwrap<Data>(result: { readonly data?: Data | undefined; readonly response: Response }): Data {
  if (result.data === undefined) {
    throw new ApiError(result.response.status);
  }

  return result.data;
}
