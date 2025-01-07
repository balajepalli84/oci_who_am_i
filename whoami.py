import oci
import sys
import json
import os


def get_user_info(profile_name="DEFAULT"):
    """
    Retrieves user information from the specified OCI profile and returns it as a JSON object.

    Args:
      profile_name: The name of the profile in the OCI config file.
                     Defaults to "DEFAULT".

    Returns:
      A JSON object containing the user information (name and OCID), or an error message
      if an exception occurs.
    """
    try:
        # Load configuration from the specified profile
        config = oci.config.from_file(profile_name=profile_name)

        # Check for authentication_type
        if "authentication_type" in config and config["authentication_type"] == "instance_principal":
            # Use OCI_CS_USER_OCID from environment variables if available
            user_ocid = os.getenv("OCI_CS_USER_OCID")
            if not user_ocid:
                raise ValueError("OCI_CS_USER_OCID environment variable is not set for instance_principal.")
        else:
            # Use the user from the configuration
            user_ocid = config["user"]

        # Get the user agent from environment variables
        user_agent = os.getenv("OCI_SDK_APPEND_USER_AGENT", "local")

        # Create an IdentityClient
        identity_client = oci.identity.IdentityClient(config)

        # Get the user information
        user = identity_client.get_user(user_ocid).data

        # Create a dictionary with the user information
        user_info = {
            "profile_name": profile_name,
            "user_name": user.name,
            "ocid": user.id,
            "user_agent": user_agent,
        }

        # Return the user information as a JSON object
        return json.dumps(user_info)

    except oci.exceptions.ProfileNotFound as e:
        return json.dumps({"error": f"Profile '{profile_name}' not found."})
    except Exception as e:
        return json.dumps({"error": f"An error occurred: {e}"})


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("Usage: python whoami.py [profile_name=PROFILE_NAME]")
            print("Example: python whoami.py profile_name=MY_PROFILE")
            sys.exit(0)  # Exit after displaying help
        profile_name = sys.argv[1].split("=")[1]  # Extract profile name
        user_info_json = get_user_info(profile_name=profile_name)
    else:
        user_info_json = get_user_info()

    print(user_info_json)  # Print the JSON output
