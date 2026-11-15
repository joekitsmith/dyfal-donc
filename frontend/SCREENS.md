# Screens

Every screen the app has: its route, what it is for, the states it can be in and what a person can do on it. The design pass starts from this file, so a change to a screen's states or actions is a change here too.

## Front door `/`

Sends people where they belong, and shows "Loading" until it knows. This becomes the home screen.

| State                     | Shown                       |
| ------------------------- | --------------------------- |
| Checking who is signed in | Loading                     |
| Signed in                 | Moves to the lesson         |
| Signed out                | Moves to the welcome screen |

## Welcome `/welcome`

For someone who is signed out. Starting needs no sign-up.

Actions: **Try it now** (starts a guest account and opens the lesson), **Sign in with a passkey**, **Use a recovery code** (opens the recovery screen).

| State                       | Shown                                                                         |
| --------------------------- | ----------------------------------------------------------------------------- |
| Checking who is signed in   | Loading                                                                       |
| Idle                        | The two actions                                                               |
| Working                     | Both actions disabled while a request or the browser's passkey prompt is open |
| Signed in already           | Moves to the lesson                                                           |
| Prompt dismissed            | A neutral message that nothing changed                                        |
| Passkey not recognised      | An error that suggests another passkey or a guest start                       |
| Browser cannot use passkeys | "Sign in with a passkey" is hidden, with a message                            |
| Server error                | A general error                                                               |

## Lesson `/learn`

The learning loop for the signed-in learner. Signed-out visitors are sent to the welcome screen.

Actions: **Start**, **Missed it** (also M), **Pause or Resume** (Space), **Replay** (R), skip the outcome window (N), change the think-time slider, open **Account**. Guests also get **Add a passkey** and **Not now** on the save prompt.

| State                                 | Shown                                                                                                         |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| Checking who is signed in             | Loading                                                                                                       |
| Idle                                  | Start                                                                                                         |
| Loading the next exercise             | The English line empty, Start gone                                                                            |
| Preparing the clips                   | The same, while the audio is fetched                                                                          |
| Playing the English                   | The English text                                                                                              |
| Thinking                              | A bar fills over the think time, with Missed it available                                                     |
| Waiting for the Welsh clip            | The bar is full, and the Welsh is still coming                                                                |
| Playing the Welsh                     | The Welsh text appears when the pause between the two Welsh clips ends and stays for the rest of the exercise |
| Playing the slow Welsh                | The slow clip plays                                                                                           |
| Awaiting the outcome                  | A short window to mark the exercise missed                                                                    |
| Submitting                            | The outcome is being sent                                                                                     |
| Paused                                | Any playing or waiting state, held                                                                            |
| Nothing to give                       | A message that there is a gap in the course                                                                   |
| Error                                 | A message that says why when it is known (speech down, progress missing), and Retry when retrying can help    |
| Signed out partway                    | The learner is sent to the welcome screen                                                                     |
| Guest with 5 or more items introduced | The save prompt above the exercise, until dismissed or saved                                                  |
| Just saved                            | A short confirmation that the passkey works from any device                                                   |

The progress counts (introduced, learning, in review, due) show once they have loaded.

## Recover `/recover`

For someone who lost their passkey and has a recovery code. Each code works once.

Actions: enter a code and **Sign in**, **Back**, then **Add a new passkey** and **Continue to the lesson**.

| State                                          | Shown                                                                                     |
| ---------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Checking who is signed in                      | Loading                                                                                   |
| Already signed in, and did not just use a code | Moves to the lesson                                                                       |
| Idle                                           | The code field. Dashes, spaces and capitals do not matter                                 |
| Empty code                                     | A message under the field                                                                 |
| Signing in                                     | The button is disabled                                                                    |
| Code wrong, or already used                    | One message for both                                                                      |
| Server error                                   | A general error                                                                           |
| Signed in with the code                        | A success message asking for a new passkey, the add-passkey form and a link to the lesson |

## Recovery codes dialog

Shown over any screen, once, after a person's first passkey is saved or new codes are made. The codes live only in memory until the dialog closes.

Actions: **Copy**, **Download**, tick **I have saved these codes**, then **Done**.

| State             | Shown                                                                   |
| ----------------- | ----------------------------------------------------------------------- |
| Hidden            | Nothing                                                                 |
| Showing           | The ten codes, which cannot be dismissed with Escape or a click outside |
| Copied            | The copy button says so                                                 |
| Not yet confirmed | Done is disabled                                                        |

## Account `/account`

Who is signed in and how they get back in.

Actions: **Back to the lesson**, **Add a passkey** (for a guest), **Add another passkey** with an optional name, **Remove** a passkey, **Make new codes** (with a confirmation that the old ones stop working), **Sign out**, **Delete account**.

| State                                                                       | Shown                                                             |
| --------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| Loading                                                                     | Loading                                                           |
| Guest                                                                       | "You are using a guest account", the save prompt, and no passkeys |
| Account with passkeys                                                       | The passkey list, with when each was added and last used          |
| Only one passkey                                                            | No Remove on it, because it is the only way back in               |
| Several passkeys                                                            | Remove on each                                                    |
| Signing out as a guest                                                      | A confirmation first: there is no way back in                     |
| Deleting                                                                    | A confirmation first: everything is deleted                       |
| Prompt dismissed, passkey already saved, browser unsupported, other failure | The same messages as the welcome screen                           |
| Signed out                                                                  | Moves to the welcome screen                                       |
