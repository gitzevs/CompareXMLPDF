from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def generate_cv_policy(output_filename, username, policy_number, premium):
    """Generates a PDF CV Policy with provided details."""
    c = canvas.Canvas(output_filename, pagesize=letter)
    c.setFont("Helvetica", 12)

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 750, "Comprehensive Vehicle Policy")

    # Subtitle
    c.setFont("Helvetica-Oblique", 12)
    c.drawString(200, 730, "Policy Document")
    c.line(200, 728, 400, 728)

    # User details
    c.setFont("Helvetica", 12)
    text_y = 700
    c.drawString(72, text_y, f"Policy Holder Name: {username}")
    c.drawString(72, text_y - 20, f"Policy Number: {policy_number}")
    c.drawString(72, text_y - 40, f"Premium Amount: ${premium}")

    # Policy details
    text_y -= 80
    c.setFont("Helvetica-Bold", 14)
    c.drawString(72, text_y, "Policy Terms and Conditions:")
    text_y -= 20
    c.setFont("Helvetica", 12)
    policy_text = [
        "1. The policy covers all vehicles listed under the policyholder's ownership.",
        "2. The premium is due annually based on the evaluation of risks.",
        "3. Comprehensive coverage includes accidental damage, theft, and third-party liability.",
        "4. Any dispute arising from the policy is subject to state laws.",
        "Please read the terms and conditions in your policy document for further details."
    ]

    # Write policy details
    for line in policy_text:
        c.drawString(72, text_y, line)
        text_y -= 15  # Line spacing

    # Footer
    text_y -= 20
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(72, text_y, "Generated with care by the Insurance Management System")

    # Save the file
    c.save()

# Generate the first CV Policy
generate_cv_policy("cv_policy1.pdf", "John Doe", "12345ABC", "500")

# Generate the second CV Policy with a slight variation
generate_cv_policy("cv_policy2.pdf", "Jane Smith", "67890XYZ", "550")