class Solution:
    def __init__(self, val=None):
        self.root = {}

    def addWord(self, word: str) -> None:
        curr = self.root
        for char in word:
            if char not in curr:
                curr[char] = {}
            curr = curr[char]
        curr.setdefault("end", True)

    def wordBreak(self, s: str, wordDict: [str]) -> bool:
        # create a trie for all words in wordDict.
        for word in wordDict:
            self.addWord(word)
        # check if word can be collected from the trie.
        curr = self.root
        for char in s:
            if char in curr:
                curr = curr[char]
            else:
                return False
            if "end" in curr:
                curr = self.root
        return True


# s = "leetcode"
# wordDict = ["leet", "code"]
s = "aaaaaaa"
wordDict = ["aaaa", "aa"]
trie = Solution()
print(trie.wordBreak(s, wordDict))
