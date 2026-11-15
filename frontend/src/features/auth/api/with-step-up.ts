import { askToConfirm } from "../stores/step-up-store";
import { isStepUpRequired } from "../utils/step-up";

/**
 * Makes a request that changes the account. If the server asks for a recent sign-in, the person is
 * asked to confirm with their passkey and the request is made once more.
 */
export async function withStepUp<Result>(request: () => Promise<Result>): Promise<Result> {
  try {
    return await request();
  } catch (error) {
    if (!isStepUpRequired(error)) {
      throw error;
    }

    await askToConfirm();

    return request();
  }
}
