# // Using a PDF -> Image conversion for full, accurate
# // context etraction from PDFs


from openai import OpenAI
import tiktoken

# https://community.openai.com/t/whats-the-tokenization-algorithm-gpt-4-1-uses/1245758
scheme = "o200k_base"  # << gpt-4.1 uses same as 4o
enc = tiktoken.get_encoding(scheme)

enc_out = enc.encode("Hello, world!")


# Compare tokens accross Images vs PDFs
