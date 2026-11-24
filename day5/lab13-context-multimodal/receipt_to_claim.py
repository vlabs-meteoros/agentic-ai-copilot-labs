"""
Lab 13, Task 6 - Multi-modal AI from Python: an image AND text in one request.

Sends a receipt image plus the expense policy to the shared Azure OpenAI deployment (gpt-4.1-mini can read
images), and gets back a Pydantic-checked draft claim. Then it checks the model's arithmetic in plain Python.

    python day5\\lab13-context-multimodal\\receipt_to_claim.py                  # the Chamundi Coffee Works receipt
    python day5\\lab13-context-multimodal\\receipt_to_claim.py --no-image       # same request WITHOUT the image
    python day5\\lab13-context-multimodal\\receipt_to_claim.py --image other.png --employee E01

Reads AZURE_AI_ENDPOINT, AZURE_AI_KEY and AZURE_OPENAI_DEPLOYMENT from the repository's .env (same values as Day 2 and Day 4).
"""
import argparse
import base64
import os
import sys
from pathlib import Path
from typing import Literal

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from dotenv import load_dotenv
from pydantic import BaseModel, Field

LAB_DIR = Path(__file__).resolve().parent
APP_DIR = LAB_DIR.parent / "kavericlaims"           # the pristine copy of the app in the labs repository
DEFAULT_IMAGE = APP_DIR / "receipts" / "CCW-2026-11873.png"
POLICY_FILE = APP_DIR / "specs" / "policy.md"

for _folder in [Path.cwd(), *Path.cwd().parents][:4]:
    if (_folder / ".env").exists():
        load_dotenv(_folder / ".env", override=True)
        break


# ------------------------------------------------------------------ The shape we want back
# Field descriptions are part of the JSON schema the model must follow, so they are written for the model.
class ReceiptLine(BaseModel):
    item: str = Field(description="The item exactly as printed on the receipt")
    amount: float = Field(description="The line amount before tax, as printed")
    claimable: bool = Field(description="True if this line can be claimed as a MEAL under the policy")
    reason: str = Field(description="Why the line is or isn't claimable, in at most 12 words")


class DraftClaim(BaseModel):
    merchant: str
    invoice_number: str
    date: str = Field(description="The receipt date as YYYY-MM-DD")
    city: str = Field(description="The city of the merchant, for example Mysuru")
    currency: str = Field(description="ISO currency code, for example INR")
    lines: list[ReceiptLine] = Field(description="Every item line on the receipt, in order. No tax or total lines")
    subtotal: float = Field(description="The subtotal before tax, as printed")
    tax_total: float = Field(description="All tax on the receipt added together")
    receipt_total: float = Field(description="The grand total, as printed")
    claimable_amount: float = Field(description="The claimable lines plus their share of the tax, rounded to 2 decimals")
    category: Literal["MEAL", "HOTEL", "TRAVEL", "INTERNET", "OTHER"]
    # TODO (Lab 13, Task 6): add one field here, then run the script again


BUILT_IN_FIELDS = {"merchant", "invoice_number", "date", "city", "currency", "lines", "subtotal",
                   "tax_total", "receipt_total", "claimable_amount", "category"}


def get_llm_client():
    """Return (client, deployment) for the Azure OpenAI v1 API on the shared resource (same as Day 2 and Day 4)."""
    from openai import OpenAI

    def setting(*names, default=None):
        for name in names:
            value = os.getenv(name, "").strip()
            if value and not value.startswith("<"):
                return value
        return default

    endpoint = setting("AZURE_OPENAI_ENDPOINT", "AZURE_AI_ENDPOINT")
    key = setting("AZURE_OPENAI_API_KEY", "AZURE_AI_KEY")
    deployment = setting("AZURE_OPENAI_DEPLOYMENT", default="gpt-4.1-mini")
    if not endpoint or not key:
        raise SystemExit("AZURE_AI_ENDPOINT / AZURE_AI_KEY are missing from .env (see Day 2, Lab 6, Task 1).")
    client = OpenAI(base_url=endpoint.rstrip("/") + "/openai/v1/", api_key=key, max_retries=5)
    return client, deployment


def image_as_data_url(path: Path) -> str:
    """Return the image as a data: URL, the simplest way to send a local image in a chat request."""
    mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}.get(path.suffix.lower())
    if not mime:
        raise SystemExit(f"Unsupported image type: {path.suffix} (use .png, .jpg or .webp)")
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def build_messages(policy: str, employee: str, image: Path | None) -> list[dict]:
    """One system message, and one user message whose content is a LIST of parts: text, then (optionally) the image."""
    instructions = (
        f"Employee {employee} claims this receipt from a business breakfast meeting with a client.\n"
        "Read the receipt, decide which lines are claimable as a MEAL under the policy, and fill in the draft claim.\n"
        "Copy numbers exactly as printed. If you can't see a receipt, leave text fields empty and numbers 0."
    )
    parts = [{"type": "text", "text": instructions}]
    if image is not None:
        parts.append({"type": "image_url", "image_url": {"url": image_as_data_url(image), "detail": "high"}})
    return [
        {"role": "system", "content": "You help Kaveri Systems employees file expense claims.\n\n" + policy},
        {"role": "user", "content": parts},
    ]


def check_arithmetic(claim: DraftClaim) -> float:
    """Recompute the claimable amount in Python from the lines the model read. Never trust a model's arithmetic."""
    subtotal = sum(line.amount for line in claim.lines)
    claimable = sum(line.amount for line in claim.lines if line.claimable)
    tax_share = claim.tax_total * claimable / subtotal if subtotal else 0.0
    expected = round(claimable + tax_share, 2)
    print("\nChecking the model's numbers in Python:")
    print(f"  lines add up to         {subtotal:10.2f}   (receipt subtotal {claim.subtotal:.2f})"
          f"  {'OK' if abs(subtotal - claim.subtotal) < 0.01 else '<-- DIFFERENT'}")
    print(f"  claimable lines         {claimable:10.2f}")
    print(f"  their share of the tax  {tax_share:10.2f}")
    print(f"  claimable amount        {expected:10.2f}   (model said {claim.claimable_amount:.2f})"
          f"  {'OK' if abs(expected - claim.claimable_amount) <= 0.01 else '<-- DIFFERENT: use the Python number'}")
    return expected


def main():
    parser = argparse.ArgumentParser(description="Read a receipt image into a draft expense claim.")
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--employee", default="E06 (Kavya Shetty, grade G2)")
    parser.add_argument("--claim-id", default="C-1125")
    parser.add_argument("--no-image", action="store_true", help="send the same request without the image")
    args = parser.parse_args()

    image = None if args.no_image else args.image
    if image is not None and not image.exists():
        raise SystemExit(f"No such image: {image}")
    client, deployment = get_llm_client()
    messages = build_messages(POLICY_FILE.read_text(encoding="utf-8"), args.employee, image)

    print(f"Sending to {deployment}: the policy as text" + (f" + the image {image.name}" if image else " (NO image)") + " ...")
    r = client.chat.completions.parse(model=deployment, messages=messages, response_format=DraftClaim, temperature=0)
    claim = r.choices[0].message.parsed

    print(f"\n{claim.merchant} | invoice {claim.invoice_number} | {claim.date} | {claim.city} | {claim.currency}")
    for line in claim.lines:
        mark = "CLAIM" if line.claimable else "  -  "
        print(f"  [{mark}] {line.item:<24} {line.amount:9.2f}   {line.reason}")
    print(f"  subtotal {claim.subtotal:.2f} + tax {claim.tax_total:.2f} = total {claim.receipt_total:.2f}")
    extra = {k: v for k, v in claim.model_dump().items() if k not in BUILT_IN_FIELDS}
    if extra:
        print("  your new field(s):", extra)

    amount = check_arithmetic(claim)
    emp_id = args.employee.split()[0]
    print("\nDraft row for data/claims_2026-11.csv (check it before you use it):")
    print(f"{args.claim_id},{emp_id},{claim.date},{claim.category},{claim.city},{amount:.2f},{claim.currency},1,"
          f"{(image.name if image else '')},submitted,Client breakfast at {claim.merchant.title().replace(',', '')}")
    print(f"\n[tokens: {r.usage.prompt_tokens} in + {r.usage.completion_tokens} out]")


if __name__ == "__main__":
    main()
