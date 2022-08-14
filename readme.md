# Reverse Entropy Clock

This module implements logical clocks as well as HybridTime and some
experimental clock mechanisms.

## Overview

Time synchronization between nodes in a distributed system is a difficult and
often intractable problem. While some amount of synchronization is possible
between physical clocks, there will always be some level of error that increases
with time as the clocks drift. The result is that timestamps created from the
physical clocks of nodes to track causal relationships between events is
unreliable. Several logical clocks have been constructed to overcome this
synchronization issue and provide partial or total ordering of events,
preserving causal relationships. This module implements several such clocks.

### Scalar Clock (Lamport Timestamp Algorithm)

Leslie Lamport introduced the logical clock concept to computer science in 1978
with his paper, "Time, clocks, and the ordering of events in a distributed
system". All nodes in a distributed system using the Lamport timestamp algorithm
share a monotonic clock where the timestamp is a single scalar value; every time
a message is sent, the scalar value is incremented and attached as a timestamp;
every time a message is received, the maximum of the current value and the
attached value is incremented and set as the clock value; every time a node
generates an event, it increments the clock value and attaches it to the event
as a timestamp. The clock monotonically moves forward to logically track causal
chains of events using a single scalar value.

### Vector Clocks

The vector clock is an extension of the scalar clock concept. However, instead
of sharing a single scalar between all nodes/processes, a vector is created in
which every node has its own scalar clock. The whole vector is included as the
timestamp for any event/message. When a message is received, each scalar in the
timestamp is compared with the coresponding scalar in the local vector clock,
and each scalar in the local clock is set to the maximum of the timestamp scalar
and the local scalar. Each scalar element is only incremented by events created
on the node corresponding to that scalar (i.e. position in the vector). This
system allows for partial ordering of events and detection of causal links. The
size of timestamps scales linearly with the number of nodes, and the vector
configuration is not dynamic, making this scheme unsuitable for systems with
large numbers of nodes or dynamic system membership.

However, the vector clock concept can be extended in several ways to solve both
the scalability and dynamic membership issues.

### Map Clocks

The map clock is an extension of the vector clock concept. In this system, each
node has a unique ID, and the clock maps IDs to scalars. Dynamic membership can
be attained by combining this map with an ORSet CRDT; a coordinator or set of
coordinators should be used for updating the ORSet. Without the ORSet to remove
crashed or departed nodes, the size of the timestamp will have unbounded growth.

To the author's knowledge, this is a novel extension of the vector clock system.

### Chain Clocks

Chain clocks were introduced in 2005 by Agarwal and Garg in their paper
"Efficient Dependency Tracking for Relevant Events in Concurrent Systems". They
introduced three types of chain clocks: the Dynamic Chain Clock (DCC), the
Antichain-based Chain Clock (ACC), and the Variable-based Chain Clock (VCC). All
three will be implemented in this module.

#### Dynamic Chain Clock

@todo

#### Antichain-based Chain Clock

@todo

#### Variable-based Chain Clock

@todo

### HybridTime Clocks

The original HybridTime algorithm id described "Technical Report: HybridTime -
Accessible Global Consistency with High Clock Uncertainty" by Alves et al. This
algorithm is similar to the Lamport logical clock and is composed of two parts:
a physical timestamp and a logical timestamp. When a message is received, the
node compares local time to the received time; if the local time is higher, the
HT time component becomes the local time and the scalar is set to 0; if the
received time is higher, the HT time component becomes the received time and the
HT scalar component becomes the received HT scalar component and incremented.
This produces a monotonically increasing clock with correspondence to physical
time and logical tracking of causality.

A further development presented by Jon Moore at the Strange Loop Conference,
"How to Have Your Causality and Wall Clocks, Too", introduces prepending an
epoch counter to reset the physical time component to recover correlation to
physical time after a node gets its physical clock anomalously out of sync. This
then is the combination of three scalars: the epoch, the monotonic Unix
timestamp, and the logical component. In this talk, Moore also presented a
protocol for clock synchronization that piggybacks on normal network traffic to
converge upon the median clock for the cluster.

The underlying assumptions in the original HybridTime specification were
1. Machines have reasonably accurate physical clocks that provide absolute time
measurements;
2. Machines periodically synchronize to a reference clock, such as by NTP; and
3. Machines have a reasonable estimate of the error range with respect to the
reference clock, such as provided by NTP.

The additional assumption for the Epochal HybridTime system is that machines
which anomalously desynchronize will eventually be corrected. If median clocks
are used instead of a reference clock server, desynchronization detection and
recalibration can be automatic and not require manual intervention even when the
source of the desynchronization was user error and/or NTP fails.

This module includes an implementation without epochs and an implemenation with
epochs. Both include methods for calculating offsets and synchronizing to the
median offset, but there are no methods for generating or exchanging the packets
for this process.


## Status

- [ ] Readme
- [ ] Tests
- [ ] Interfaces
- [ ] Scalar Clock
- [ ] Vector Clock
- [ ] Map Clock
- [ ] Dynamic Chain Clock
- [ ] Antichain-based Chain Clock
- [ ] Variable-based Chain Clock
- [ ] HybridTime Clock
- [ ] HybridEpoch Clock
- [ ] Optimizations

## Installation

Currently, this project is still in development, so the best way to install is
to clone the repo and then run the following from within the root directory
(assuming a Linix terminal):

```
python -m venv venv/
source venv/bin/activate
pip install -r requirements.txt
```

On Windows, you may have to run `source venv/Scripts/activate` instead
of `source venv/bin/activate`.

To run the MapClock example with ACL rules, also run
`pip install -r optional_requirements.txt`.

These instructions will change once development is complete and the module is
published as a package.

## Classes and Interfaces

### Interfaces

- ClockProtocol(Protocol)
- ChainClockProtocol(Protocol)
- HybridTimeProtocol(Protocol)

### Classes

- ScalarClock(ClockProtocol)
- VectorClock(ClockProtocol)
- MapClock(ClockProtocol)
- DynamicChainClock(ClockProtocol)
- AntichainChainClock(ClockProtocol)
- VariableChainClock(ClockProtocol)
- HybridClock(HybridTimeProtocol)
- HybridEpochClock(HybridTimeProtocol)

## Examples

Examples can be found in the `examples/` folder. To run all the examples, the
optional requirements must be installed as described above.

## Tests

Open a terminal in the `tests` directory and run the following:

```
python -m unittest
```

The tests are the interface contract that the code follows. Examples of intended
behaviors are contained in those files. Reading through them may be helpful when
reasoning about the clock mechanisms.

## Bugs

If you encounter a bug, please submit an issue on GitHub.

## ISC License

Copyleft (c) 2022 k98kurz

Permission to use, copy, modify, and/or distribute this software
for any purpose with or without fee is hereby granted, provided
that the above copyleft notice and this permission notice appear in
all copies.

Exceptions: this permission is not granted to Alphabet/Google, Amazon,
Apple, Microsoft, Netflix, Meta/Facebook, Twitter, or Disney; nor is
permission granted to any company that contracts to supply weapons or
logistics to any national military; nor is permission granted to any
national government or governmental agency; nor is permission granted to
any employees, associates, or affiliates of these designated entities.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE
AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR
CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
