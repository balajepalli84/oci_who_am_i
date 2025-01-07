import oci
import sys
import json
import os
import subprocess


def get_user_info(profile_name="DEFAULT"):
    """
    Retrieves user information from the specified OCI profile or instance metadata and returns it as a JSON object.

    Args:
      profile_name: The name of the profile in the OCI config file.
                     Defaults to "DEFAULT".

    Returns:
      A JSON object containing the user information (name and OCID), or an error message
      if an exception occurs.
    """
    try:
        # Check if the config file exists
        config_file_path = os.path.expanduser(oci.config.DEFAULT_LOCATION)
        if not os.path.exists(config_file_path) and not os.getenv("OCI_CS_USER_OCID"):
            config = None
        else:
            try:
                # Attempt to load configuration from the specified profile
                config = oci.config.from_file(profile_name=profile_name)
            except oci.exceptions.ProfileNotFound:
                config = None

        user_info = {}
        if config:
            # Check for authentication_type
            if "authentication_type" in config and config["authentication_type"] == "instance_principal":
                # Use OCI_CS_USER_OCID from environment variables if available
                user_ocid = os.getenv("OCI_CS_USER_OCID")
                if not user_ocid:
                    raise ValueError("OCI_CS_USER_OCID environment variable is not set for Cloud Shell.")
                user_agent = "Cloud_Shell"
            else:
                # Use the user from the configuration
                user_ocid = config["user"]
                user_agent = os.getenv("OCI_SDK_APPEND_USER_AGENT", "local")

            # Create an IdentityClient
            identity_client = oci.identity.IdentityClient(config)

            # Get the user information
            user = identity_client.get_user(user_ocid).data

            # Populate user_info from API
            user_info = {
                "profile_name": profile_name,
                "user_name": user.name,
                "ocid": user.id,
                "user_agent": user_agent,
            }
        else:
            # Fallback: Check instance metadata
            metadata = subprocess.check_output(
                ["curl", "-s", "-L", "http://169.254.169.254/opc/v1/instance/"],
                universal_newlines=True
            )
            metadata_json = json.loads(metadata)
            user_info = {
                "ocid": metadata_json.get("id"),
                "displayName": metadata_json.get("displayName"),
                "region": metadata_json.get("region"),
                "compartmentId": metadata_json.get("compartmentId"),
                "user_agent": "instance_principal",
            }

        # Return the user information as a JSON object
        return json.dumps(user_info)
    except subprocess.CalledProcessError:
        return json.dumps({"error": "Unable to retrieve instance metadata. Ensure this script is running on an OCI instance."})
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
