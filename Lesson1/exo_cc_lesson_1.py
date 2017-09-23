import unittest


# Given a string and a non-negative int n, return a larger string
# that is n copies of the original string.

def string_times(string, n):
    return n * string


# Given an array of ints, return True if one of the first 4 elements
# in the array is a 9. The array length may be less than 4.
def array_front9(nums):
    # longueur=min(len(nums) & 4)
    return (len(nums) > 3) and (9 in nums[:4])


# Given a string, return the count of the number of times
# that a substring length 2 appears  in the string and also as
# the last 2 chars of the string, so "hixxxhi" yields 1 (we won't count the end substring).
def last2(string):
    # If non overlapping substrings, this works fine :
    #    return string.count(string[-2:], 0, -2)

    # else use this thing
    if len(string) < 2:
        return

    pattern = string[-2:]
    total = 0
    for i in range(len(string) - 3):
        if string[i: i + 2] == pattern:
            total += 1
    return total


# Write a program that maps a list of words into a list of
# integers representing the lengths of the correponding words.
def length_words(array):
    return [len(word) for word in array]


# write fizbuzz programm
def fizbuzz(n):
    return "\n".join("Fizz" * (i % 3 == 0) + "Buzz" * (i % 5 == 0) or str(i) for i in range(1, n))


# Write a function that takes a number and returns a list of its digits.
def number2digits(number):
    return [int(c) for c in str(number)]


# Write function that translates a text to Pig Latin and back.
# English is translated to Pig Latin by taking the first letter of every word,
# moving it to the end of the word and adding 'ay'
def pigLatin(text):
    return " ".join([word[1:] + word[0] + "ay" for word in text.split()]).capitalize()


# Write a proramm that returna dictionary of occurences of the alphabet for a given string.
# Test it with the Lorem upsuj
# "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
def occurences(text):
    to_return = {}
    for c in text:
        if str.isalpha(c):
            if c in to_return:
                to_return[c] += 1
            else:
                to_return[c] = 1
    return to_return


# Here's our "unit tests".
class Lesson1Tests(unittest.TestCase):
    fizbuzz(101)

    def testArrayFront9(self):
        self.assertEqual(array_front9([1, 2, 9, 3, 4]), True)
        self.assertEqual(array_front9([1, 2, 3, 4, 9]), False)
        self.assertEqual(array_front9([1, 2, 3, 4, 5]), False)

    def testStringTimes(self):
        self.assertEqual(string_times('Hel', 2), 'HelHel')
        self.assertEqual(string_times('Toto', 1), 'Toto')
        self.assertEqual(string_times('P', 4), 'PPPP')

    def testLast2(self):
        self.assertEqual(last2('hixxhi'), 1)
        self.assertEqual(last2('xaxxaxaxx'), 1)
        self.assertEqual(last2('axxxaaxx'), 2)

    def testLengthWord(self):
        self.assertEqual(length_words(['hello', 'toto']), [5, 4])
        self.assertEqual(length_words(['s', 'ss', '59fk', 'flkj3']), [1, 2, 4, 5])

    def testNumber2Digits(self):
        self.assertEqual(number2digits(8849), [8, 8, 4, 9])
        self.assertEqual(number2digits(4985098), [4, 9, 8, 5, 0, 9, 8])

    def testPigLatin(self):
        self.assertEqual(pigLatin("The quick brown fox"), "Hetay uickqay rownbay oxfay")


def main():
    unittest.main()


if __name__ == '__main__':
    main()
