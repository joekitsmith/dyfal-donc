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

Actions: **Start**, **Missed it** (also M), **Pause or Resume** (Space), **Replay** (R), skip the outcome window (N), open **Account** or **Settings**. Guests also get **Add a passkey** and **Not now** on the save prompt.

| State                                              | Shown                                                                                                                                            |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| Checking who is signed in, or loading the settings | Loading                                                                                                                                          |
| Idle                                               | Start                                                                                                                                            |
| Loading the next exercise                          | The English line empty, Start gone                                                                                                               |
| Preparing the clips                                | The same, while the audio is fetched                                                                                                             |
| Playing the English                                | The English text                                                                                                                                 |
| Thinking                                           | A bar fills over the think time, with Missed it available                                                                                        |
| Waiting for the Welsh clip                         | The bar is full, and the Welsh is still coming                                                                                                   |
| Playing the Welsh                                  | The woman's clip plays. The text appears when the pause between the two Welsh clips ends and the man starts, or straight away with standard only |
| Playing the slow Welsh                             | The man's clip plays. With slow only, this is the only Welsh, and the text appears as it starts                                                  |
| Awaiting the outcome                               | A short window to mark the exercise missed                                                                                                       |
| Submitting                                         | The outcome is being sent                                                                                                                        |
| Paused                                             | Any playing or waiting state, held                                                                                                               |
| Nothing to give                                    | A message that there is a gap in the course                                                                                                      |
| Error                                              | A message that says why when it is known (speech down, progress missing), and Retry when retrying can help                                       |
| Signed out partway                                 | The learner is sent to the welcome screen                                                                                                        |
| Guest with 5 or more items introduced              | The save prompt above the exercise, until dismissed or saved                                                                                     |
| Just saved                                         | A short confirmation that the passkey works from any device                                                                                      |

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

## Confirm it is you dialog

Shown over any screen when the server wants a sign-in just now before it changes an account: adding a passkey, making new recovery codes, removing a passkey or deleting the account. A guest is never asked, because a guest has nothing to confirm with. The change goes ahead once the person confirms.

Actions: **Confirm with passkey**, **Cancel**.

| State                                                   | Shown                                                                   |
| ------------------------------------------------------- | ----------------------------------------------------------------------- |
| Hidden                                                  | Nothing                                                                 |
| Asking                                                  | The explanation and both actions                                        |
| Confirming                                              | Confirm is disabled while the browser's passkey prompt is open          |
| Prompt dismissed, passkey not recognised, other failure | The same messages as the welcome screen                                 |
| Confirmed with another account's passkey                | The person is now signed in as that account, and the change is not made |

## Account `/account`

Who is signed in and how they get back in.

Actions: **Back to the lesson**, open **Settings**, **Add a passkey** (for a guest), **Add another passkey** with an optional name, **Remove** a passkey, **Make new codes** (with a confirmation that the old ones stop working), **Sign out**, **Delete account**.

| State                                                                       | Shown                                                                                                        |
| --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| Loading                                                                     | Loading                                                                                                      |
| Guest                                                                       | "You are using a guest account", the save prompt, and no passkeys                                            |
| Account with passkeys                                                       | The passkey list, with when each was added and last used                                                     |
| Only one passkey                                                            | No Remove on it, because it is the only way back in                                                          |
| Several passkeys                                                            | Remove on each                                                                                               |
| Signing out as a guest                                                      | A confirmation first: there is no way back in                                                                |
| Deleting                                                                    | A confirmation first: everything is deleted                                                                  |
| Prompt dismissed, passkey already saved, browser unsupported, other failure | The same messages as the welcome screen                                                                      |
| Signed out                                                                  | Moves to the welcome screen. An account's session also ends 30 days after it began, however much it was used |

## Settings `/settings`

How the lesson behaves for this person. Signed-out visitors are sent to the welcome screen. The settings belong to the account, so they follow a person to any device.

Actions: change a setting, **Save**, **Back to the lesson**.

| Setting     | Control                                                               | Effect                                                                                            |
| ----------- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| Think time  | Slider from 0.5× to 3×                                                | Scales how long there is to say the Welsh                                                         |
| Welsh audio | Choice: standard then slow (the default), standard only, or slow only | Which Welsh recordings play after the think time. The Welsh text appears when the last one starts |

| State                         | Shown                                                    |
| ----------------------------- | -------------------------------------------------------- |
| Loading                       | Loading                                                  |
| Idle                          | The saved settings                                       |
| Changed, not saved            | The form is edited, and nothing is saved until Save      |
| Saving                        | Save is disabled                                         |
| Saved                         | A confirmation, until the next change                    |
| Could not save                | An error, with the edits kept so Save can be tried again |
| Could not load, or signed out | An error, or a move to the welcome screen                |
