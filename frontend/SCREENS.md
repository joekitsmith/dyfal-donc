# Screens

Every screen the app has: its route, what it is for, the states it can be in and what a person can do on it. The design pass starts from this file, so a change to a screen's states or actions is a change here too.

## Home `/`

Where a signed-in person lands. Signed-out visitors are sent to the welcome screen.

Actions: **Start learning** or **Continue learning** (opens the lesson), **See details** on the recap, open **Course**, **Settings** or **Account**. Guests also get **Add a passkey** and **Not now** on the save prompt once they have a recap.

| State                                           | Shown                                                                                                                             |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| Checking who is signed in                       | Loading                                                                                                                           |
| Brand-new learner                               | No recap, the counts at zero, and Start learning                                                                                  |
| Session ended (last answer over 10 minutes ago) | "Last time": the number of exercises, how long it lasted, and the new words, in Welsh and English. The button says Start learning |
| Session still going                             | "This session so far", the same details, and the button says Continue learning                                                    |
| Words due                                       | How many items are due for review now                                                                                             |
| Nothing due                                     | "Nothing to review right now"                                                                                                     |
| New words ready                                 | The topic the next new words belong to                                                                                            |
| Course finished                                 | "You have met every word in the course"                                                                                           |
| Guest with a recap                              | The save prompt                                                                                                                   |
| Server error                                    | A general error                                                                                                                   |
| Signed out                                      | Moves to the welcome screen                                                                                                       |

A learning session is a run of answers with no pause longer than 10 minutes. There is nothing to start or end: it begins with the first answer after a pause and is over once 10 minutes pass without one.

## Learning session summary `/learning-sessions/[id]`

What a person did in one learning session. The id is the number of the session's first answer, so it never changes once the session has begun.

Actions: **Back to home**, open any new word or word that slipped, **Play** and **Play slowly** on each missed exercise, **Keep going** (while the session is still going) or **Start another**.

| State                     | Shown                                                                                                           |
| ------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Loading                   | Loading                                                                                                         |
| Normal                    | The number of exercises, how long, and "still going" if it is                                                   |
| Reviewed words            | How many words they already knew were practised                                                                 |
| New words                 | Each in Welsh and English, linking to its page, or no section if there are none                                 |
| Words that slipped        | Words that were in long-term review and were missed (each linking to its page), or no section if there are none |
| Missed exercises          | The English, the Welsh and the two Play buttons, or no section if there are none                                |
| Audio could not be played | An error under the missed exercises                                                                             |
| No such session           | A message that it does not exist, and Back to home                                                              |
| Signed out                | Moves to the welcome screen                                                                                     |

## Course `/course`

Where the learner has got to, and a way to look up anything they have met. Nothing here is a score: there are no percentages, strengths or targets, and nothing about words not yet met.

Actions: **Back to home**, **search** the box, open a started topic, **Play** and **Play slowly** on a sentence, open a word or phrase.

| State                     | Shown                                                                                                                                                                   |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Loading                   | Loading                                                                                                                                                                 |
| Brand-new learner         | "Words and sentences appear here as you meet them", and every topic under "Later in the course"                                                                         |
| Started topic             | An accordion with the topic name, "Current" on the topic being learned, and "12 words · 4 ways of saying things · 42 exercises answered". The current topic opens first |
| Inside a started topic    | Things you can say (up to five sentences they got right, each with Play and Play slowly), then Words, then Ways of saying things, each linking to its page              |
| Topics not started        | Their names only, under "Later in the course", in teaching order. They cannot be opened and show no counts or words                                                     |
| Searching                 | A flat list of the words and phrases met whose English, Welsh or other forms match, ignoring case and accents, each with its topic. It replaces the topics              |
| Search finds nothing      | "Nothing you have met matches that"                                                                                                                                     |
| Audio could not be played | An error under the sentences                                                                                                                                            |
| Server error              | A general error                                                                                                                                                         |
| Signed out                | Moves to the welcome screen                                                                                                                                             |

## Word or phrase `/course/items/[id]`

One word or phrase the learner has met.

Actions: **Back to the course**, **Play** (words only), **Play** and **Play slowly** on each sentence.

| State                     | Shown                                                                                                                                                                                      |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Loading                   | Loading                                                                                                                                                                                    |
| Word                      | The Welsh, the English, "Word", Play, other forms and notes if there are any, and the day it was first met                                                                                 |
| Phrase                    | The pattern with its slot, the English, "Way of saying things", "The part in [brackets] is where a word goes", notes, and the day it was first met. No Play: its sentences carry the audio |
| Sentences                 | Up to five sentences containing it that they got right, newest first, each with Play and Play slowly; none shown if they have not got one right yet                                        |
| Not found                 | "We could not find that word", and Back to the course. Not met and not existing look the same                                                                                              |
| Audio could not be played | An error under the item                                                                                                                                                                    |
| Signed out                | Moves to the welcome screen                                                                                                                                                                |

## Welcome `/welcome`

For someone who is signed out. Starting needs no sign-up.

Actions: **Try it now** (starts a guest account and opens the home screen), **Sign in with a passkey**, **Use a recovery code** (opens the recovery screen).

| State                       | Shown                                                                         |
| --------------------------- | ----------------------------------------------------------------------------- |
| Checking who is signed in   | Loading                                                                       |
| Idle                        | The two actions                                                               |
| Working                     | Both actions disabled while a request or the browser's passkey prompt is open |
| Signed in already           | Moves to the home screen                                                      |
| Prompt dismissed            | A neutral message that nothing changed                                        |
| Passkey not recognised      | An error that suggests another passkey or a guest start                       |
| Browser cannot use passkeys | "Sign in with a passkey" is hidden, with a message                            |
| Server error                | A general error                                                               |

## Lesson `/learn`

The learning loop for the signed-in learner. Signed-out visitors are sent to the welcome screen.

Actions: **Start**, **Missed it** (also M), **Pause or Resume** (Space), **Replay** (R), skip the outcome window (N), open **Home**, **Account** or **Settings**. Guests also get **Add a passkey** and **Not now** on the save prompt.

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

The progress counts (introduced, learning, in review, due) show once they have loaded. A clock shows how long the learning session has been going, from the first answer after a pause, and stays out of the way (it is not a limit and nothing happens when it passes any time).

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
