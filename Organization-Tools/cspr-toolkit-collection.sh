#!/bin/bash

# This is intended to be an automated approach for implamenting the
# Cloud Security Posture Review Toolkit Prerequisite Customer Guide
# data collection.
#

# Verify Bash compatability version
BASH_MAJOR_MINOR=$( echo $BASH_VERSION | cut -d. -f1-2 )
if (( $( echo "$BASH_MAJOR_MINOR < 5.0" | bc -l) ))
then
		(
		echo "Minimum version of bash required: 5.0"
		echo "Please update your bash version, or try from another system."
		) 1>&2
		exit 1
fi


# Functions:
function okquit() {
	read -p "${1} (yN): " ynanswer

	if [[ ! "${ynanswer,,}" =~ ^(y) ]]
	then
		if [ "${2}" != '' ]
		then
			echo -e "\n$2"
		else
			echo -e "\nAborted.  Please contact your cloud administrator if you have questions."
		fi
		exit 2
	else
		echo
		echo
	fi
}

function exitsteps() {
	# Restore default project to previous setting
	if [ "${EXISTING_DEFAULT_PROJECT}" != '' ]
	then
		gcloud config set project "${EXISTING_DEFAULT_PROJECT}" >/dev/null 2>&1
	else
		gcloud config unset project >/dev/null 2>&1
	fi

	exit 3

}

# Terminal Commands
export TERM=screen
bold=$( tput bold)
reset=$( tput sgr0)
moveuponeline=$( tput cuu1)
eraseline=$( tput el)

### Introduction
cat <<END


Your Google Cloud partner has been engaged to complete a Cloud Security Posture Review
and subsequently requires access to your Google Cloud inventory data and a Google project in your
organization to collect and review the asset data.

The purpose of this script is to:
• Set up a GCP project if one has not been done manually.
• Enable the required APIs for the project.
• Export the metadata for all Resources, IAM-Policies, Org-Policies, and Access-Policies 
   for the entire organization to the project instance of BigQuery.
• Export inventory metadata out of BigQuery to Cloud Storage.  (optional)
• Download inventory metadata from Cloud Storage, and compress into a tar.gz file.  (optional)

This script ${bold}WILL ONLY${reset} export metadata of the environment.
This export ${bold}should not${reset} be considered a backup of the environment, and could not
be used to recreate the environment data in the event of a loss.


END
okquit 'Continue?'


# Operating account
echo -e "\n\n"
cat <<END
A user account with the following permissions is required:
+--------------------------------------+---------------------+--------------------------------------+
|  Suggested Role                      |  Resource Level     |  Description                         |
+--------------------------------------+---------------------+--------------------------------------+
| roles/resourcemanager.projectCreator | Organization/Folder | The permission required to create a  |
| (Optional)                           |                     |  project with the billing account    |
+--------------------------------------+---------------------+--------------------------------------+
| roles/billing.user                   | Organization/Folder | The permission required to create a  |
| (Optional)                           |                     | project with the billing account     |
+--------------------------------------+---------------------+--------------------------------------+
| roles/cloudasset.viewer              | Organization        | The permission required to export    |
|                                      |                     |  the Cloud Asset Inventory data into |
|                                      |                     |  a BigQuery dataset                  |
+--------------------------------------+---------------------+--------------------------------------+
| roles/serviceusage.serviceUsageAdmin | Project             | The permission required to enable    |
|                                      |                     |  Cloud Asset Inventory API           |
+--------------------------------------+---------------------+--------------------------------------+
| roles/bigquery.dataEditor            | Project             | The permission required to create    |
|                                      |                     |  BigQuery datasets and tables        |
+--------------------------------------+---------------------+--------------------------------------+
| roles/bigquery.user                  | Project             | The permission required to create    |
|                                      |                     |  BigQuery datasets and tables        |
+--------------------------------------+---------------------+--------------------------------------+

END
echo -e "Existing User: ${bold}${USER_EMAIL}${reset}"
# todo: verify permissions
okquit 'Does this look correct, and does this user have the above permissions?' 'Please switch users, and restart the script.'


# Org Discovery
ORGANIZATION=$(gcloud organizations list --format="value(DISPLAY_NAME)")
ORGANIZATION_ID=$(gcloud organizations list --format="value(ID)")
if [ "$( echo $ORGANIZATION_ID | wc -w)" -gt 1 ]
then
	EXITERROR=0

	echo "Looks like you have access to multiple organizations." 1>&2
	echo "ERROR: Multiple Organizations aren't supported automatically yet!" 1>&2
	read -p "Would you like to specify your Organization, and ID? (yN): " specifyorg
	if [[ "${specifyorg,,}" =~ ^(y) ]]
	then
			gcloud organizations list --format="table[box](DISPLAY_NAME,ID)"
		read -p "Organization Display Name: " ORGANIZATION
		read -p "Organization ID: " ORGANIZATION_ID
	else
		EXITERROR=1
	fi

	if [ "${ORGANIZATION}" = '' ] && [ "${ORGANIZATION_ID}" = '' ]
	then
		EXITERROR=1
	else
		ORG_INPUT_CHECK=$(gcloud organizations describe ${ORGANIZATION_ID} --format="value(displayName)")
	fi


	if [ "${ORGANIZATION}" != "${ORG_INPUT_CHECK}" ]
	then
		EXITERROR=1
	fi

	if [ "${EXITERROR}" = 1 ]
	then
		echo "The Organization and Organization ID you entered do not match" 1>&2
		echo "Please contact your Google Cloud partner for additional support." 1>&2
		exit 5
	fi

	echo -e "\n\n"
fi
echo -e "Organization: ${bold}${ORGANIZATION}${reset}\nOrganization ID#: ${bold}${ORGANIZATION_ID}${reset}"
okquit 'Does this look correct?'


# Project Discovery
cat <<END 
It is recommended that a separate dedicated project is created and used exclusively for 
Cloud Asset Inventory data to prevent overlap, and facilitate easy cleanup.  You can manually
create a project for use by this script, or have this script create a project for you.

If you need to place the project at any level other than the top organization,
please create the project manually.

END

read -p "Would you like this script to automatically create a project for you? (yN): " projcreate
if [[ "${projcreate,,}" =~ ^(y) ]]
then
	# todo: Place project under folder
	
	# Billing Information
	BILLING_ACCOUNT=$( gcloud beta billing accounts list --format "value(ACCOUNT_ID)")
	BQ_PROJECT_NAME="$( echo ${ORGANIZATION}-cspr- | sed -e 's/\./-/g')$(tr -dc 'a-z' </dev/random | fold -w 5  | head  -1)"
	BQ_PROJECT_NAME="$( echo ${BQ_PROJECT_NAME} | cut -c 1-30)"
	echo 
	echo -e "Project name: ${bold}${BQ_PROJECT_NAME}${reset}"
	echo -e "Billing Account: ${bold}${BILLING_ACCOUNT}${reset}"
	okquit 'Does this look acceptable?' "Aborted.\nPlease create the project manually, and restart this script"
	# todo: Create option to change default name

	# Project Setup
	gcloud projects create ${BQ_PROJECT_NAME} --organization=${ORGANIZATION_ID}
	gcloud beta billing projects link ${BQ_PROJECT_NAME} --billing-account=${BILLING_ACCOUNT}

else
	echo 
	read -p "Please enter the project name you wish to use for export: " BQ_PROJECT_NAME
	echo -e "Project name: ${bold}${BQ_PROJECT_NAME}${reset}"
	okquit 'Is this correct?' 'Please restart the script with updated project name'
	# todo: Create option to re-enter project name
	# todo: verify project name
fi

BQ_PROJECT_ID=$(gcloud projects describe ${BQ_PROJECT_NAME} --format "value(projectNumber)")


# Storage Bucket
read -p "Will you be exporting this data to a Storage Bucket for sharing with your Google Cloud partner? (yN)" bucket_question
if [[ "${bucket_question,,}" =~ ^(y) ]]
then
	BUCKET_EXPORT=$( echo "${ORGANIZATION}-cspr-$(date '+%Y%m%d')-$(tr -dc 'a-z' </dev/random | fold -w 5  | head  -1)" | sed -e 's/\./_/g')
else
	BUCKET_EXPORT='<Export Disabled>'
fi

# Envrionment Values
BQDATASET_CAI=$( echo "${ORGANIZATION}_cai_$(date '+%s')" | sed -e 's/\./_/g')

# todo: list available regions: gcloud compute region list, requires compute api enabled
read -p "Region [us-central1]: " LOCATION
if [ "${LOCATION}" = '' ]
then
	LOCATION='us-central1'
fi

# Final Check
echo -e "\n\n"
echo -e "User: ${bold}${USER_EMAIL}${reset}"
echo -e "Organization: ${bold}${ORGANIZATION}${reset}"
echo -e "Organization ID#: ${bold}${ORGANIZATION_ID}${reset}"
echo -e "Project Name: ${bold}${BQ_PROJECT_NAME}${reset}"
echo -e "Project Number: ${bold}${BQ_PROJECT_ID}${reset}"
echo -e "BQ Dataset: ${bold}${BQDATASET_CAI}${reset}"
echo -e "Region: ${bold}${LOCATION}${reset}"
echo -e "Storage Bucket: ${bold}${BUCKET_EXPORT}${reset}"
okquit 'Continue?' 'Aborted'

# Trap ^C and issue cleanup commands
trap exitsteps SIGINT

# Save existing default project for environment reset later
EXISTING_DEFAULT_PROJECT=$(gcloud config get project)
# Set the default project
gcloud config set project ${BQ_PROJECT_NAME}

# Enable APIs
echo -e "Verifying/Enabling APIs...(this may take a few minutes)"
gcloud services enable bigquery.googleapis.com
gcloud services enable cloudasset.googleapis.com
gcloud services enable storage.googleapis.com

# Create new BigQuery datasets
# todo: capture error, and fail gracefully
echo -e "Creating BigQuery dataset..."
bq mk --location ${LOCATION} --project_id ${BQ_PROJECT_NAME} -d ${BQDATASET_CAI}

# Service Idenity Account
# todo: capture error, and fail gracefully
echo -e "Creating Service Idenity Account, and Permissions..."
echo "> ${bold}service-${BQ_PROJECT_ID}@gcp-sa-cloudasset.iam.gserviceaccount.com${reset}"
gcloud beta services identity create --service=cloudasset.googleapis.com \
 --project=${BQ_PROJECT_NAME}

echo "> ${bold}roles/bigquery.dataEditor${reset}"
gcloud projects add-iam-policy-binding ${BQ_PROJECT_NAME} --member \
serviceAccount:service-${BQ_PROJECT_ID}@gcp-sa-cloudasset.iam.gserviceaccount.com \
  --role roles/bigquery.dataEditor

echo "> ${bold}roles/bigquery.user${reset}"
gcloud projects add-iam-policy-binding ${BQ_PROJECT_NAME} --member \
  serviceAccount:service-${BQ_PROJECT_ID}@gcp-sa-cloudasset.iam.gserviceaccount.com \
  --role roles/bigquery.user


# Resources Export to BigQuery
# todo: capture error, and fail gracefully
echo -e "\n\n"
RESOURCE_JOB=$( gcloud asset export --billing-project ${BQ_PROJECT_NAME} \
     --content-type resource \
     --organization  ${ORGANIZATION_ID} \
     --bigquery-table projects/${BQ_PROJECT_NAME}/datasets/${BQDATASET_CAI}/tables/resource \
     --output-bigquery-force \
     --per-asset-type 2>&1)
RESOURCE_JOB_ID=$( echo ${RESOURCE_JOB} | perl -ne '($jobid)=( $_ =~ /describe ([^]]+)\]/); print "$jobid\n"')

# IAM Policy Export to BigQuery
IAM_POLICY_JOB=$( gcloud asset export --billing-project ${BQ_PROJECT_NAME} \
     --content-type iam-policy \
     --organization  ${ORGANIZATION_ID} \
     --bigquery-table projects/${BQ_PROJECT_NAME}/datasets/${BQDATASET_CAI}/tables/iam_policy \
     --output-bigquery-force 2>&1)
IAM_POLICY_JOB_ID=$( echo ${IAM_POLICY_JOB} | perl -ne '($jobid)=( $_ =~ /describe ([^]]+)\]/); print "$jobid\n"')

# Org Policy Export to BigQuery
ORG_POLICY_JOB=$( gcloud asset export --billing-project ${BQ_PROJECT_NAME} \
     --content-type org-policy \
     --organization  ${ORGANIZATION_ID} \
     --bigquery-table projects/${BQ_PROJECT_NAME}/datasets/${BQDATASET_CAI}/tables/org_policy \
     --output-bigquery-force 2>&1)
ORG_POLICY_JOB_ID=$( echo ${ORG_POLICY_JOB} | perl -ne '($jobid)=( $_ =~ /describe ([^]]+)\]/); print "$jobid\n"')

# Access Policy export to BigQuery
ACCESS_POLICY_JOB=$( gcloud asset export --billing-project ${BQ_PROJECT_NAME} \
     --content-type access-policy \
     --organization  ${ORGANIZATION_ID} \
     --bigquery-table projects/${BQ_PROJECT_NAME}/datasets/${BQDATASET_CAI}/tables/access_policy \
     --output-bigquery-force 2>&1)
ACCESS_POLICY_JOB_ID=$( echo ${ACCESS_POLICY_JOB} | perl -ne '($jobid)=( $_ =~ /describe ([^\]]+)\]/); print "$jobid\n"')

# OS-Inventory export to BigQuery
OS_INVENTORY_JOB=$( gcloud asset export --billing-project ${BQ_PROJECT_NAME} \
     --content-type os-inventory \
     --organization  ${ORGANIZATION_ID} \
     --bigquery-table projects/${BQ_PROJECT_NAME}/datasets/${BQDATASET_CAI}/tables/access_policy \
     --output-bigquery-force 2>&1)
OS_INVENTORY_JOB_ID=$( echo ${ACCESS_POLICY_JOB} | perl -ne '($jobid)=( $_ =~ /describe ([^\]]+)\]/); print "$jobid\n"')

# Relationship export to BigQuery
RELATIONSHIP_JOB=$( gcloud asset export --billing-project ${BQ_PROJECT_NAME} \
     --content-type relationship \
     --organization  ${ORGANIZATION_ID} \
     --bigquery-table projects/${BQ_PROJECT_NAME}/datasets/${BQDATASET_CAI}/tables/access_policy \
     --output-bigquery-force 2>&1)
RELATIONSHIP_JOB_ID=$( echo ${ACCESS_POLICY_JOB} | perl -ne '($jobid)=( $_ =~ /describe ([^\]]+)\]/); print "$jobid\n"')

# Monitor jobs to finish

RESOURCE_JOB_STATUS=0
IAM_JOB_STATUS=0
ORG_JOB_STATUS=0
ACCESS_JOB_STATUS=0
donecount=0
export_cycle=0
cyclesleep=2
verbose_working=1
while [ "${donecount}" -lt 6 ]
do
	width=$( tput cols); ((width=${width}-2))
	# Resource Export
	echo -e "${eraseline}Resources export...\c"
	if [ "${RESOURCE_JOB_STATUS}" = 0 ]
	then
		RESOURCE_JOB_STATUS=$( gcloud asset operations describe ${RESOURCE_JOB_ID} | egrep -c '^done: true')
		if [ "${RESOURCE_JOB_STATUS}" = 0 ]
		then
			if [ "${verbose_working}" = 0 ] ||\
			   [ "$(echo -e "Working \t ${RESOURCE_JOB_ID}" | wc -c)" -ge ${width} ]
			then
				echo -e "Working..."
			else
				echo -e "Working \t ${RESOURCE_JOB_ID}"
			fi
		else
			echo "${bold}Done${reset}"
		fi
	else
		echo "${bold}Done${reset}"
	fi

	# IAM Export
	echo -e "${eraseline}IAM Policy export...\c"
	if [ "${IAM_JOB_STATUS}" = 0 ]
	then
		IAM_JOB_STATUS=$( gcloud asset operations describe ${IAM_POLICY_JOB_ID} | egrep -c '^done: true')
		if [ "${IAM_JOB_STATUS}" = 0 ]
		then
			if [ "${verbose_working}" = 0 ] ||\
			   [ "$(echo -e "Working \t ${IAM_POLICY_JOB_ID}" | wc -c)" -ge ${width} ]
			then
				echo -e "Working..."
			else
				echo -e "Working \t ${IAM_POLICY_JOB_ID}"
			fi
		else
			echo "${bold}Done${reset}"
		fi
	else
		echo "${bold}Done${reset}"
	fi

	# ORG Export
	echo -e "${eraseline}ORG Policy export...\c"
	if [ "${ORG_JOB_STATUS}" = 0 ]
	then
		ORG_JOB_STATUS=$( gcloud asset operations describe ${ORG_POLICY_JOB_ID} | egrep -c '^done: true')
		if [ "${ORG_JOB_STATUS}" = 0 ]
		then
			if [ "${verbose_working}" = 0 ] ||\
			   [ "$(echo -e "Working \t ${ORG_POLICY_JOB_ID}" | wc -c)" -ge ${width} ]
			then
				echo -e "Working..."
			else
				echo -e "Working \t ${ORG_POLICY_JOB_ID}"
			fi
		else
			echo "${bold}Done${reset}"
		fi
	else
		echo "${bold}Done${reset}"
	fi

	# ACCESS Export
	echo -e "${eraseline}Access Policy export...\c"
	if [ "${ACCESS_JOB_STATUS}" = 0 ]
	then
		ACCESS_JOB_STATUS=$( gcloud asset operations describe ${ACCESS_POLICY_JOB_ID} | egrep -c '^done: true')
		if [ "${ACCESS_JOB_STATUS}" = 0 ]
		then
			if [ "${verbose_working}" = 0 ] ||\
			   [ "$(echo -e "Working \t ${ACCESS_POLICY_JOB_ID}" | wc -c)" -ge ${width} ]
			then
				echo -e "Working..."
			else
				echo -e "Working \t ${ACCESS_POLICY_JOB_ID}"
			fi
		else
			echo "${bold}Done${reset}"
		fi
	else
		echo "${bold}Done${reset}"
	fi


	# OS-Inventory Export
	echo -e "${eraseline}OS-Inventory export...\c"
	if [ "${OS_INVENTORY_JOB_STATUS}" = 0 ]
	then
		OS_INVENTORY_JOB_STATUS=$( gcloud asset operations describe ${OS_INVENTORY_JOB_ID} | egrep -c '^done: true')
		if [ "${OS_INVENTORY_JOB_STATUS}" = 0 ]
		then
			if [ "${verbose_working}" = 0 ] ||\
			   [ "$(echo -e "Working \t ${OS_INVENTORY_JOB_ID}" | wc -c)" -ge ${width} ]
			then
				echo -e "Working..."
			else
				echo -e "Working \t ${OS_INVENTORY_JOB_ID}"
			fi
		else
			echo "${bold}Done${reset}"
		fi
	else
		echo "${bold}Done${reset}"
	fi


	# ACCESS Export
	echo -e "${eraseline}Access Policy export...\c"
	if [ "${RELATIONSHIP_JOB_STATUS}" = 0 ]
	then
		RELATIONSHIP_JOB_STATUS=$( gcloud asset operations describe ${RELATIONSHIP_JOB_ID} | egrep -c '^done: true')
		if [ "${RELATIONSHIP_JOB_STATUS}" = 0 ]
		then
			if [ "${verbose_working}" = 0 ] ||\
			   [ "$(echo -e "Working \t ${RELATIONSHIP_JOB_ID}" | wc -c)" -ge ${width} ]
			then
				echo -e "Working..."
			else
				echo -e "Working \t ${RELATIONSHIP_JOB_ID}"
			fi
		else
			echo "${bold}Done${reset}"
		fi
	else
		echo "${bold}Done${reset}"
	fi



	# Count the successfully completed jobs
	(( donecount= ${RESOURCE_JOB_STATUS} + ${IAM_JOB_STATUS} + ${ORG_JOB_STATUS} + ${ACCESS_JOB_STATUS} + ${OS_INVENTORY_JOB_STATUS} + ${RELATIONSHIP_JOB_STATUS} ))
	if [ "${donecount}" -lt 6 ]
	then
		sleep ${cyclesleep}
		# Move cursor up five rows
		echo "${moveuponeline}${moveuponeline}${moveuponeline}${moveuponeline}${moveuponeline}${moveuponeline}${moveuponeline}"
	fi

	# Count the cycles
	((export_cycle++))

	# If the export is taking a long time, slow down the check cycle.
	if [ "${export_cycle}" -ge 60 ]
	then
		cyclesleep=5
		verbose_working=1
	fi
done


# Optional Export from BigQuery
if [ "${BUCKET_EXPORT}" != '<Export Disabled>' ]
then
	
	# Create Cloud Storage Bucket
	echo -e "Creating storage bucket..."
	gcloud storage buckets create gs://${BUCKET_EXPORT} --project=${BQ_PROJECT_NAME} \
		--location=${LOCATION} --default-storage-class=STANDARD --uniform-bucket-level-access
###
### Need to deal with error
### ERROR: (gcloud.storage.buckets.create) HTTPError 403: The billing account for the owning project is disabled in state absent
	
	# Export BigQuery dataset to Cloud Storage Bucket
	echo -e "Exporting BigQuery dataset to storage bucket... (this will take a moment)"
	for table in $(bq --project_id "${BQ_PROJECT_NAME}" ls --max_results 1000 --format=csv "${BQDATASET_CAI}" \
	| sed '1,1d' | awk -F, '{ print $2 }')
	do 
		echo -e "${table}..."
		bq extract --destination_format=AVRO ${table} gs://${BUCKET_EXPORT}/$(echo ${table} | sed 's/.*://').avro
	done
	
	
	# Download to tgz file
	echo -e "Storage bucket export size: $( gcloud storage du gs://${BUCKET_EXPORT} --summarize --readable-sizes)"
	okquit "Would you like this script to download, and tar-gz the export?" "This collection script has finished.\n• Please manually export the data from gs://${BUCKET_EXPORT} and forward to your Google Cloud partner.\n• If you would like to remove this project, please manually issue the command 'gcloud projects delete ${BQ_PROJECT_NAME}'"
	
	local_directory=$( mktemp -d)
	gsutil rsync -r gs://${BUCKET_EXPORT} ${local_directory}/
	tar -czvf ${BUCKET_EXPORT}.tar.gz  ${local_directory}/*
	
fi


echo -e "\n"
echo -e "This collection script has finished."

if [ "${BUCKET_EXPORT}" != '<Export Disabled>' ]
then
	echo -e "• The data has been downloaded to the local directory ${local_directory}."
	echo -e "  If you're executing this script in a Cloud Shell, this directory may be removed as soon as the cloud shell exits."
	echo -e "• The data compressed to the file ${BUCKET_EXPORT}.tar.gz.  Please forward this file to your Google Cloud partner."
	echo -e "• If you would like to remove this project, please manually issue the command: 'gcloud projects delete ${BQ_PROJECT_NAME}'"
	echo -e "  Removing this project will remove the asset collection data from BigQuery and Cloud Storage,"
	echo -e "  and disable all APIs enabled in this project."
else
	echo -e "• Per user decision, this data has not been exported from BigQuery."
	echo -e "• Please contact your Google Cloud partner for further processing of this asset data."
	echo -e "• If you choose to remove this project, please manually issue the command: 'gcloud projects delete ${BQ_PROJECT_NAME}'"
	echo -e "  Removing this project without manually exporting, or sharing the data with your Google Cloud partner will"
	echo -e "  also delete the asset collection data captured during this script session."
fi

# Reset the environment
exitsteps



exit 0


