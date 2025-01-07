import oci
import sys
import json

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

        # Create an IdentityClient
        identity_client = oci.identity.IdentityClient(config)
        #print(f"config is {config}")
        # Get the user information
        user = identity_client.get_user(config["user"]).data

        # Create a dictionary with the user information
        user_info = {
            "profile_name": profile_name,
            "user_name": user.name,
            "ocid": user.id
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
