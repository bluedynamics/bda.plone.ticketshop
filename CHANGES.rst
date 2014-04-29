Changelog
=========


1.0dev
------

- Add event subscriber for Ticket, which listens on worflow state changes. The
  subscriber applies the workflow transition of the Ticket to any contained
  Ticket Occurrences, if possible.
  [thet]

- initial work.
  [rnix, thet]
