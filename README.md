# Event Scheduler

## General Flow:
1. Host user creates new `Event`
2. Host user adds other users ,`members`, to `Event`
3. Host user suggests `EventTime`'s
4. Event's `members` are presented with list of `EventTime`'s
5. If an `EventTime` works for all members:
   1. Schedule the event for all `members` and host user.
   2. Notify all relevant users
6. If no `EventTime` works for all members:
   1. Ask for suggested `EventTime`
   2. Check suggested `EventTime` against all other `members` `Availability`'s
   3. If no constraints, ask other `members`

## Challenges:
1. Importing contacts
   * [You probably can't from a webapp](https://stackoverflow.com/questions/24076800/can-a-website-html5-javascript-access-a-mobile-devices-android-iphone-conta)
   * Import from WhatsApp/Line/etc?
   * Manually input numbers? (barf)
   * Make mobile app? (barf)
2. Sending SMS messages from django
   * [Twilio seems easy to implement](https://www.youtube.com/watch?v=KYQ3u3xDPRA)