

# Delete one letter of character from string
#   Inputs: text, example: "ETH-USD"
#           delete_char, example: "-"
#   Output: text, example: "ETHUSD"
def delete_char(text, delete_char):
    return text.replace(delete_char, "")
