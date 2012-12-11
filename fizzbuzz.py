"""Slightly overengineered FizzBuzz implementation

Spec::

    Write a program that prints the numbers from 1 to 100. But for
    multiples of three print 'Fizz' instead of the number and for the
    multiples of five print 'Buzz'. For numbers which are multiples of
    both three and five print 'FizzBuzz'.

This spec is from
http://imranontech.com/2007/01/24/using-fizzbuzz-to-find-developers-who-grok-coding/,
which I believe is the original source that was later popularized by
http://www.codinghorror.com/blog/2007/02/why-cant-programmers-program.html

This implementation uses a simple rule processor to find the FizzBuzz
numbers. Yes, this is slightly ridiculous, but it was fun.

Test::

    python -m unittest fizzbuzz

    and

    python -m doctest fizzbuzz.py

Run::

    python fizzbuzz.py

    or

    python -m fizzbuzz

"""


class RuleSet(object):

    r"""Container for an ordered set of rules.

    Each rule has a condition and an action to be taken if that
    condition is matched. Each value that is processed will be tested
    against the rules in the order the rules were added to the rule set.
    If a value matches a "last" rule, no further rules will be checked
    for that value (this is similar to the L flag in an Apache
    RewriteRule).

    Default actions can be specified as well. These are actions that
    will be executed for any input that doesn't match at least one rule.
    Default actions will be executed in the order they are added to the
    rule set.

    A rule set knows nothing about the values it processes; likewise,
    the data being processed would typically be unware of the rule set.

    Usage::

        >>> import sys; write = sys.stdout.write
        >>> rules = RuleSet()
        >>> # The following rule matches the exact string "a".
        >>> rules.add(
        ...     lambda x: x == 'a',
        ...     lambda x: write('Found an a!\n'),
        ...     last=True)
        >>> # This rule matches strings that both start and end with
        >>> # "a". This *would* match the string "a" except that the
        >>> # rule above prevents that (because `last=True`).
        >>> rules.add(
        ...     lambda x: x.startswith('a') and x.endswith('a'),
        ...     lambda x: write('Found an a...a!\n'))
        >>> rules.process('a')
        Found an a!
        >>> rules.process('axxxa')
        Found an a...a!
        >>> # Nothing happens for "b" because there's no rule and no
        >>> # default.
        >>> rules.process('b')
        >>> # Let's add a default rule and process several items at
        >>> # once.
        >>> rules.add_default(lambda x: write('Unknown: {0}\n'.format(x)))
        >>> rules.process_many(['axxxa', 'a', 'b'])
        Found an a...a!
        Found an a!
        Unknown: b

    """

    def __init__(self, before_processing=None, after_processing=None):
        """

            ``before_processing``
                A function that will be called before every value is
                processed. It will be passed the value that is about to
                be processed. Its purpose is to provide a place to do
                anything that needs to happen before every value is
                processed.

            ``after_processing``
                Like ``before_processing`` but called after every value
                is processed.

        """
        self._rules = []
        self._defaults = []
        self.before_processing = before_processing
        self.after_processing = after_processing

    def add(self, condition, action, last=False):
        """Add a rule.

        ``condition``
            A function that takes a single argument and returns `True`
            or `False`.

        ``action``
            A function that takes a single argument (the same one that
            is passed to ``condition``) and does something with it.

        ``last``
            When this is `True`, when a value matches this rule no
            further rules will be processed.

        """
        self._rules.append(Rule(condition, action, last))

    def add_default(self, action):
        """Add a default action.

        Default actions are executed for values that don't match at
        least one rule.

        ``action`` is as described in :meth:`add`.

        """
        self._defaults.append(action)

    def process(self, x):
        """Test if ``x`` matches rule(s) and execute action(s) if so."""
        match_not_found = True
        if self.before_processing:
            self.before_processing(x)
        for rule in self._rules:
            if rule.matches(x):
                rule.action(x)
                match_not_found = False
                if rule.last:
                    break
        if match_not_found:
            for action in self._defaults:
                action(x)
        if self.after_processing:
            self.after_processing()

    def process_many(self, xs):
        for x in xs:
            self.process(x)


class Rule(object):

    def __init__(self, condition, action, last=False):
        self.condition = condition
        self.action = action
        self.last = last

    def matches(self, x):
        """Test whether the value ``x`` matches this rule."""
        return self.condition(x)


def get_fizz_buzz_values():
    """For N in [1, 100], return the corresponding FizzBuzz list.

    The values in the FizzBuzz list are determined according to these
    rules::

        - if N is a multiple of 3 => "Fizz"
        - if N is a multiple of 5 => "Buzz"
        - if N is a multiple of both 3 and 5 => "FizzBuzz"
        - otherwise => original value

    """
    output = []
    rules = RuleSet()
    rules.add(
        lambda x: x % 15 == 0, lambda x: output.append('FizzBuzz'), last=True)
    rules.add(lambda x: x % 3 == 0, lambda x: output.append('Fizz'))
    rules.add(lambda x: x % 5 == 0, lambda x: output.append('Buzz'))
    rules.add_default(lambda x: output.append(x))
    rules.process_many(range(1, 101))
    return output


if __name__ == '__main__':
    print('\n'.join(str(v) for v in get_fizz_buzz_values()))


import unittest


class TestFizzBuzz(unittest.TestCase):

    def test_output(self):
        output = get_fizz_buzz_values()
        for v in output:
            if isinstance(v, int):
                self.assertNotEqual(v % 3, 0)
                self.assertNotEqual(v % 5, 0)
        text = open('fizzbuzz.txt').read().strip()
        expected = text.splitlines()
        self.assertEqual([str(v) for v in output], expected)
