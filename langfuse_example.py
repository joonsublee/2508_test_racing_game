import os
import time
from langfuse.decorators import observe, langfuse_context
from langfuse.openai import openai

# 1. Set up Langfuse environment variables
# Get keys for your project from the project settings page in Langfuse
# https://cloud.langfuse.com
# Replace with your actual keys and host
os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-lf-..."
os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-..."
os.environ["LANGFUSE_HOST"] = "https://cloud.langfuse.com"

# 2. Set up your OpenAI API key
# Replace with your actual key
os.environ["OPENAI_API_KEY"] = "sk-..."

# This is a prerequisite for the Langfuse SDK to work.
# It checks if the credentials are valid.
# It will raise an exception if the auth check fails.
assert langfuse_context.auth_check()

@observe()
def simple_function():
    """A simple function that just waits for a second."""
    print("Executing simple_function...")
    time.sleep(1)
    print("simple_function finished.")
    return "Success"

@observe()
def summarize_story(story: str):
    """
    This function takes a story and uses OpenAI to summarize it.
    The @observe decorator automatically traces this function call.
    The OpenAI integration will automatically trace the API call.
    """
    print("Executing summarize_story...")
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes stories in one sentence."},
            {"role": "user", "content": story},
        ],
        temperature=0,
    )
    summary = completion.choices[0].message.content
    print("summarize_story finished.")
    return summary

@observe()
def main():
    """
    The main function that orchestrates the other functions.
    This will be the root trace in Langfuse.
    """
    print("Executing main function...")
    simple_function()

    story = (
        "The old man and the sea is a short novel written by the American author Ernest Hemingway in 1951 in Cayo Blanco, Cuba. "
        "It was the last major work of fiction by Hemingway that was published during his lifetime. "
        "One of his most famous works, it tells the story of Santiago, an aging Cuban fisherman who struggles with a giant marlin far out in the Gulf Stream off the coast of Cuba."
    )
    summary = summarize_story(story)

    print(f"\nSummary:\n{summary}")

    # You can enrich the trace with more information
    langfuse_context.update_current_trace(
        name="my-first-trace",
        user_id="test-user",
        session_id="test-session-123",
        tags=["example", "python-sdk"],
    )
    print("main function finished.")


if __name__ == "__main__":
    main()
    # Flush the Langfuse client to ensure all traces are sent before the script exits.
    # This is especially important in short-lived environments like serverless functions.
    langfuse_context.flush()
    print("\nTrace sent to Langfuse. Check your project to see the results.")
