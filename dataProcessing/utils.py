from pymongo import MongoClient
import logging
import json
import random
from bson import ObjectId
import re
import csv

def connect_to_collection(db_name, collection_name):
    try:
        client = MongoClient('Your_URL')
        _db = client[db_name]
        _collection = _db[collection_name]
        return _collection
    except Exception as exc:
        logging.error({
            "message": "Failed to connect to the collection",
            "erro": exc
        })
        raise Exception

def format_list_strings(input_list):
    if not input_list:
        return ""

    if len(input_list) == 1:
        return input_list[0]

    result = ", ".join(input_list[:-1])

    result += f" and {input_list[-1]}"

    return result
    
def add_line_numbers(input_string):
    lines = input_string.split('\n')
    max_width = len(str(len(lines)))

    formatted_lines = []
    for i, line in enumerate(lines, start=1):
        line_number = str(i).rjust(max_width)
        formatted_lines.append(f"{line_number}: {line}")

    result_string = '\n'.join(formatted_lines)
    return result_string

GITHUB_TAINT_CI_LIST = [
    r"github\.event\.issue\.title",
    r"github\.event\.issue\.body",

    r"github\.event\.discussion\.title",
    r"github\.event\.discussion\.body",
    r"github\.event\.comment\.body",
    r"github\.event\.review\.body",
    r"github\.event\.pages.*\.page_name",

    r"github\.event\.commits.*\.message",
    r"github\.event\.commits.*\.author\.email",
    r"github\.event\.commits.*\.author\.name",
    
    r"github\.event\.head_commit\.message",
    r"github\.event\.head_commit\.author\.email",
    r"github\.event\.head_commit\.author\.name",
    r"github\.event\.head_commit\.committer\.email",

    r"github\.event\.workflow_run\.head_branch",
    r"github\.event\.workflow_run\.head_commit\.message",
    r"github\.event\.workflow_run\.head_commit\.author\.email",
    r"github\.event\.workflow_run\.head_commit\.author\.name",
    
    r"github\.event\.pull_request\.title",
    r"github\.event\.pull_request\.body",
    r"github\.event\.pull_request\.head\.label",

    r"github\.head_ref",
    r"github\.event\.pull_request\.head\.ref",
    r"github\.event\.workflow_run\.pull_requests.*\.head\.ref",
    
    r"github\.event\.head_commit\.committer\.name",
    r"github\.event\.review_comment\.body",
]

GITHUB_TAINT_LIST = [
    "github.event.issue.title",
    "github.event.issue.body",

    "github.event.discussion.title",
    "github.event.discussion.body",
    "github.event.comment.body",
    "github.event.review.body",
    "github.event.pages.*.page_name",

    "github.event.commits.*.message",
    "github.event.commits.*.author.email",
    "github.event.commits.*.author.name",
    
    "github.event.head_commit.message",
    "github.event.head_commit.author.email",
    "github.event.head_commit.author.name",
    "github.event.head_commit.committer.email",

    "github.event.workflow_run.head_branch",
    "github.event.workflow_run.head_commit.message",
    "github.event.workflow_run.head_commit.author.email",
    "github.event.workflow_run.head_commit.author.name",
    
    "github.event.pull_request.title",
    "github.event.pull_request.body",
    "github.event.pull_request.head.label",

    "github.head_ref",
    "github.event.pull_request.head.ref",
    "github.event.workflow_run.pull_requests.*.head.ref",
    
    "github.event.head_commit.committer.name",
    "github.event.review_comment.body",
]

GITHUB_TAINT_CI_OBJECT_LIST = [
    "github.event.comment",
    
    "github.event.issue.pull_request",
    "github.event.issue",

    "github.event.pull_request",
    "github.event.pull_request.requested_teams",
    "github.event.pull_request.commits",
    "github.event.pull_request.head.repo",
    "github.event.pull_request.labels",
   
    "github.event.commits",
    
    "github.event.workflow_run",
    "github.event.workflow_run.pull_requests",
]

def is_taint_source(str : str):
    for regexstr in GITHUB_TAINT_CI_LIST:
        if re.match(regexstr, str):
            return True
    if str in GITHUB_TAINT_CI_OBJECT_LIST:
        return True
    return False

reusable_wf_direct_taint = [
    "opencv/ci-gha-workflow/.github/workflows/OCV-PR-4.x-iOS.yaml@main",
    "opencv/ci-gha-workflow/.github/workflows/OCV-PR-4.x-docs.yaml@main",
    "cloud-tek/build/.github/workflows/dotnet.yml@main",
    "pharmaverse/admiralci/.github/workflows/spellcheck.yml@main",
    "pharmaverse/admiralci/.github/workflows/r-pkg-validation.yml@main",
    "erzz/workflows/.github/workflows/container.yml@main",
    "mParticle/mparticle-workflows/.github/workflows/pr-title-check.yml@stable",
    "opencv/ci-gha-workflow/.github/workflows/OCV-PR-4.x-Android.yaml@main",
    "fmidev/.github/.github/workflows/docker-build-and-push.yml@0.1.6",
    "mParticle/mparticle-workflows/.github/workflows/pr-title-check.yml@main",
    "XNXKTech/workflows/.github/workflows/lark-notification.yml@main",
    "erzz/workflows/.github/workflows/source-protection.yml@main",
    "bjw-s/container-images/.github/workflows/pr-metadata.yaml@main",
    "VirtoCommerce/.github/.github/workflows/publish-docker.yml@v3.200.14",
    "pahrens-github/github-actions-requests/.github/workflows/get-action-from-issue.yml@main",
    "erzz/workflows/.github/workflows/semantic-release.yml@main",
    "pharmaverse/admiralci/.github/workflows/man-pages.yml@main",
    "iotaledger/identity.rs/.github/workflows/shared-release.yml@main",
    "opencv/ci-gha-workflow/.github/workflows/OCV-PR-4.x-U20-Cuda.yaml@main",
    "VirtoCommerce/.github/.github/workflows/deploy-cloud.yml@v3.200.14",
    "opencv/ci-gha-workflow/.github/workflows/OCV-PR-4.x-U20.yaml@main",
    "rstudio/shiny-workflows/.github/workflows/routine.yaml@v1",
    "pharmaverse/admiralci/.github/workflows/pkgdown.yml@main",
    "k8s-at-home/charts/.github/workflows/pr-metadata.yaml@master",
    "fmidev/.github/.github/workflows/update-openshift-application-version.yml@0.1.6",
    "rstudio/education-workflows/.github/workflows/auto-pkg-maintenance.yaml@v1",
    "opencv/ci-gha-workflow/.github/workflows/OCV-PR-4.x-macOS-ARM64.yaml@main",
    "pharmaverse/admiralci/.github/workflows/readme-render.yml@main",
    "akarthik10/charts/.github/workflows/pr-metadata.yaml@master",
    "opencv/ci-gha-workflow/.github/workflows/OCV-PR-4.x-ARM64.yaml@main",
    "openhie/empty-fhir-ig/.github/workflows/main.yml@master",
    "VirtoCommerce/.github/.github/workflows/deploy.yml@v3.200.7",
    "WordPress/wordpress-develop/.github/workflows/slack-notifications.yml@trunk",
    "mParticle/mparticle-workflows/.github/workflows/pr-branch-check-name.yml@stable",
    "opencv/ci-gha-workflow/.github/workflows/OCV-PR-4.x-macOS-x86_64.yaml@main",
    "opencv/ci-gha-workflow/.github/workflows/OCV-timvx-backend-tests-4.x.yml@main",
    "erzz/workflows/.github/workflows/node-tests.yml@main",
    "fmidev/.github/.github/workflows/helm-build-and-publish-to-github.yml@0.1.6",
    "pharmaverse/admiralci/.github/workflows/check-templates.yml@main",
    "mParticle/mparticle-workflows/.github/workflows/pr-branch-check-name.yml@main",
    "VirtoCommerce/.github/.github/workflows/publish-docker.yml@v3.200.7",
    "grafana/code-coverage/.github/workflows/code-coverage.yml@v0.1.12",
    "pharmaverse/admiralci/.github/workflows/r-cmd-check.yml@main",
    "rest-for-physics/framework/.github/workflows/validation.yml@master",
    "pbs/pycaption/.github/workflows/main.yml@main",
    "rajbos/github-actions-requests/.github/workflows/get-action-from-issue.yml@main",
    "cloud-tek/hive/.github/workflows/nuke.yml@main",
    "blockscout/blockscout-ci-cd/.github/workflows/e2e_new.yaml@master",
    "pharmaverse/admiralci/.github/workflows/code-coverage.yml@main",
    "VirtoCommerce/.github/.github/workflows/deploy.yml@v3.200.14",
    "opencv/ci-gha-workflow/.github/workflows/OCV-PR-4.x-W10.yaml@main",
    "pharmaverse/admiralci/.github/workflows/style.yml@main",
    "pharmaverse/admiralci/.github/workflows/lintr.yml@main",
    "onedr0p/containers/.github/workflows/pr-metadata.yaml@main"
]

reusable_wf_indirect_taint = {
    "fluent/fluent-bit-ci/.github/workflows/call-run-performance-test.yaml@main": ['git-branch']
}

composite_action_direct_taint = [  
    "emmyoop/changie_bot@v1.0.1",
    "tj-actions/branch-names@v5.1",
    "tj-actions/branch-names@v4.3",
    "embano1/wip@d10268b325aea84ff49ff3f0983c0ebc14976caf",
    "awshole/snyk-node@main",
    "CleverShuttle/gh-composite-actions/actions/merge-to-nonprod@v1",
    "bytedeco/javacpp-presets/.github/actions/deploy-centos@actions",
    "emmyoop/changie_bot@v1.0",
    "blendthink/elixir@v2",
    "tj-actions/branch-names@v5.4",
    "rlespinasse/github-slug-action@v4.3.2",
    "dmsi-io/gha-prep-release@main",
    "Dmitriy129/moodle-github-sync-1@0.1.3",
    "svanherk/test-action/visual-diff@main",
    "MetaMask/action-require-additional-reviewer@v1.0.2",
    "wayou/turn-issues-to-posts-action@v1",
    "wmde/dependabot-gerrit-action@main",
    "tj-actions/branch-names@63b65253bc9542d36a60646299bd8c9af6d9ce7e",
    "ruffinjr/testRepository@v2.0.1",
    "zhangt2333/action-judger@main",
    "jmarrec/rubocop-composite-action@v1",
    "CleverShuttle/gh-composite-actions/actions/rebase-nonprod@v1",
    "jahia/jahia-modules-action/slack-jahia@v2",
    "tj-actions/branch-names@v5.2",
    "chanzuckerberg/napari-hub-preview-action@v0.1.4",
    "impresscms-dev/phpdocs-wiki-update-action@v2.2",
    "embano1/wip@e83c03c8f4696b0cef273d83115521b26ebb8bec",
    "APN-Pucky/fast-forward-action@main",
    "andersinno/kolga-setup-action@v2",
    "cbush/snooty-autobuilder-check@main",
    "gilzow/retrieve-psh-prenv-url@main",
    "SJSU-Dev2/SJSU-Dev2v3/actions/run_tests@main",
    "tj-actions/branch-names@v5",
    "tj-actions/branch-names@v5.5",
    "tj-actions/branch-names@v6.1",
    "CumulusDS/workflow-setup-action@v1",
    "datalad/release-action/add-changelog-snippet@master",
    "rawestmoreland/heroku-review-app-actions@v2.0.2-dev-7",
    "ministryofjustice/github-actions/code-formatter@v7",
    "ominatechnologies/actions/tag@main",
    "rlespinasse/github-slug-action@4.2.4",
    "hazelcast/github-jira-tool-action@v3.2.0",
    "tj-actions/branch-names@v6",
    "bytedeco/javacpp-presets/.github/actions/redeploy@actions",
    "tj-actions/branch-names@v5.6",
    "dsb-norge/github-actions/ci-cd/create-build-envs@v1",
    "farhatahmad/branch-names@v2",
    "davoudarsalani/action-notify@master",
    "bytedeco/javacpp-presets/.github/actions/redeploy@master",
    "embano1/wip@v1",
    "tj-actions/branch-names@v4.9",
    "tj-actions/branch-names@v4.8",
    "smartlyio/github-actions@release-action-node-v1",
    "9sako6/imgcmp@v2.0.1",
    "dentarg/gem-compare@v1",
    "rlespinasse/github-slug-action@v4.x",
    "team-gsri/actions-arma-tools/release-mission@v0",
    "chanzuckerberg/napari-hub-preview-action@v0.1.5",
    "bytedeco/javacpp-presets/.github/actions/deploy-ubuntu@actions",
    "bytedeco/javacpp-presets/.github/actions/deploy-centos@master",
    "cloud-tek/actions/auto-release@0.19",
    "arwynfr/actions-conventional-versioning@v0.4",
    "tfso/gh-action-helpers/npm-build@v1.8.0",
    "arwynfr/actions-conventional-versioning@0.1.0",
    "vcu-swim-lab/bug-aimbot-action@v1.0.1",
    "rlespinasse/github-slug-action@v4.3.0",
    "bytedeco/javacpp-presets/.github/actions/deploy-macosx@actions",
    "team-gsri/actions-arma-tools/release-mod@v0",
    "calamares/actions/generic-checkout@330c45ae1eb6efad4ad75a6dd887c3c5d5fe1590",
    "cloud-tek/actions/auto-release@0.12",
    "tj-actions/branch-names@v4",
    "insightsengineering/coverage-action@v2.1.2",
    "jeanmn/github-actions/actions/notify-on-fail-or-fix@main",
    "arwynfr/actions-conventional-versioning@0.2.1",
    "duplocloud/ghactions-finish-gitflow-release@master",
    "ministryofjustice/github-actions/code-formatter@main",
    "tj-actions/branch-names@v6.2",
    "tj-actions/branch-names@v2.2",
    "neohelden/actions-library/kustomize-diff@main",
    "tj-actions/branch-names@v4.5",
    "tj-actions/branch-names@v2",
    "MetaMask/action-require-additional-reviewer@v1",
    "shrinktofit/github-app-interactive-rush@master",
    "ministryofjustice/github-actions/code-formatter@v6",
    "openpeerpower/actions/helpers/version@main",
    "yasslab/idobata_notify@main",
    "kkorolyov/publish-gradle@0.4.0",
    "dentarg/gem-compare@main",
    "sbmthakur/packj.dev@main",
    "9sako6/imgcmp@master",
    "penske-media-corp/github-action-wordpress-test-setup@main",
    "ruffinjr/testRepository@v2.0.2",
    "PiwikPRO/actions/go/test@master",
    "ubuntu/sync-issues-github-jira@v1",
    "arwynfr/actions-conventional-versioning@master",
    "hazelcast/github-jira-tool-action@v2",
    "tj-actions/branch-names@9cd06d955f4184031cd71fbb1717ac268ade2ee0",
    "bonitasoft/bonita-documentation-site/.github/actions/build-and-publish-pr-preview/@master",
    "tj-actions/branch-names@b90df97be1c548ac9c8bd9186bfea6747153bf5e",
    "platformsh/gha-retrieve-psh-prenv-url@main",
    "Kraken-Devs/branch-names@v6",
    "sfeir-open-source/sfeir-school-github-action-dev/.github/actions/runs-using-composite@main",
    "Drassil/action-package-version-bump@main",
    "anyone-developer/anyone-push-back-repo@main",
    "milanmk/actions-file-deployer@1.2",
    "krzwro/automated-release-action@v0.2.1",
    "synergy-au/pmd-analyser-action@v1",
    "xrtk/upm-release@main",
    "home-assistant/actions/helpers/version@master",
    "synergy-au/eslint-action@v1",
    "9sako6/imgcmp@v2.0.2",
    "fabriziocacicia/keep-history-conventional@v0.1.0",
    "tj-actions/branch-names@b0f914ba0e7aa1e243b53df97447f71eb57da09a",
    "0leaf/issue-to-md-posting@main",
    "bytedeco/javacpp-presets/.github/actions/deploy-windows@actions",
    "tj-actions/branch-names@09ab61130975078eb7cde103fe8d2ae1649a1853",
    "rlespinasse/github-slug-action@v4",
    "BrightspaceUI/actions/visual-diff@main",
    "rlespinasse/github-slug-action@33cd7a701db9c2baf4ad705d930ade51a9f25c14",
    "rlespinasse/github-slug-action@4.2.5",
    "sualeh/prepare-maven-build@v1.3.1",
    "hazelcast/github-jira-tool-action@v3",
    "rlespinasse/github-slug-action@4.2.3",
    "insightsengineering/coverage-action@v2",
    "jskrzypek/set-git-branch-action@1.0.0",
    "codeready-toolchain/toolchain-cicd/publish-operators-for-e2e-tests@master",
    "milanmk/actions-file-deployer@master"
]

composite_action_indirect_taint = {
    "DFE-Digital/github-actions/AddTrelloComment@master": ['CARD'],
    "tarantool/checkpatch/.github/actions/checkpatch@master": ['revision-range'],
    "codeready-toolchain/toolchain-cicd/publish-operators-for-e2e-tests@master": ['gh-head-ref'],
    "ixxmu/turn-issues-to-posts-action@master": ['title', 'comment'],
    "0chain/actions/deploy-0chain@master": ['zwallet_cli_branch', 'zbox_cli_branch'],
    "0chain/actions/run-system-tests@master": ['zwallet_cli_branch', 'zbox_cli_branch'],
    "wayou/turn-issues-to-posts-action@v1.2.5": ['title', 'body'],
    "cloudify-cosmo/cloudify-comment-action@v1.2": ['comment'],
    "synthetik-technologies/actions/composites/upload-azure-deployment@2-separate-versioning-and-docker-building": ['labels'],
    "rest-for-physics/framework/.github/actions/build@master": ['branch'],
    "junxnone/turn-issues-to-posts-action@master": ['title', 'body'],
    "GuillaumeFalourd/git-commit-push@v1.3": ['commit_message'],
    "tlienart/xranklin-build-action@v3.2": ['CLEAR_CACHE'],
    "xamarin/backport-bot-action@v1.0": ['comment_body'],
    "emmyoop/changie_bot@v1.0": ['commit_message'],
    "junxnone/issue2geojson@main": ['title', 'body'],
    "yykamei/actions-git-push@main": ['branch'],
    "junxnone/timeline_issue2md@main": ['title', 'body'],
    "reloc8/action-choose-release-version@1.0.0": ['source-branch'],
    "bonitasoft/bonita-documentation-site/.github/actions/build-pr-site/@master": ['build-preview-command'],
    "wayou/turn-issues-to-posts-action@v1": ['title', 'body'],
    "johngeorgewright/regex-action@v1.1.0": ['ref'],
    "ahmadiesa-abu/cloudify-comment-action@master": ['comment'],
    "tlienart/xranklin-build-action@v2": ['CLEAR_CACHE'],
    "rajyraman/powerapps-checker@v1.4": ['branch'],
    "junxnone/wiki_issue2md@main": ['title', 'body'],
    "ivanmilov/telegram_notify_action@v1": ['message'],
    "manuelht/action-issue2post@master": ['title', 'body'],
    "bonitasoft/bonita-documentation-site/.github/actions/build-and-publish-pr-preview/@master": ['build-preview-command'],
    "xamarin/backport-bot-action@v1.1": ['comment_body'],
    "ZenHubHQ/best-git-sha-action@v1.3": ['github_head_ref'],
    "zhangt2333/action-judger@main": ['script'],
    "overhead-actions/live-preview-frp@main": ['domain']
}
    
hardcoded_wrong_type_4 = {
    ObjectId('63dd9657045fe2c0b716429a'): [{
        "type" : "e",
        "reusable_workflow" : "WordPress/wordpress-develop/.github/workflows/slack-notifications.yml@trunk",
        # link: https://github.com/WordPress/wordpress-develop/blob/trunk/.github/workflows/slack-notifications.yml#L150
        # has a taint source github.event.head_commit.message
    }],
    ObjectId('63dd94b080aa29a6fd486d65'): [{
        "type" : "e",
        "reusable_workflow" : "rest-for-physics/framework/.github/workflows/validation.yml@master",
        # link: https://github.com/rest-for-physics/framework/blob/master/.github/workflows/validation.yml, totally 6
        # has a taint source github.head_ref
    }],
    ObjectId('63dd962e045fe2c0b71640d1'): [{
        "type" : "e",
        "reusable_workflow" : "opencv/ci-gha-workflow/.github/workflows/OCV-PR-4.x-ARM64.yaml@main",
        # link: https://github.com/opencv/ci-gha-workflow/blob/main/.github/workflows/OCV-PR-4.x-ARM64.yaml, totally 6
        # has a taint source github.head_ref
    },{
        "type" : "e",
        "reusable_workflow" : "opencv/ci-gha-workflow/.github/workflows/OCV-PR-4.x-U20.yaml@main",
        # link: https://github.com/opencv/ci-gha-workflow/blob/main/.github/workflows/OCV-PR-4.x-U20.yaml, totally 6
        # has a taint source github.head_ref
    },{
        "type" : "e",
        "reusable_workflow" : "opencv/ci-gha-workflow/.github/workflows/OCV-PR-4.x-W10.yaml@main",
        # link: https://github.com/opencv/ci-gha-workflow/blob/main/.github/workflows/OCV-PR-4.x-W10.yaml, totally 6
        # has a taint source github.head_ref
    },{
        "type" : "e",
        "reusable_workflow" : "opencv/ci-gha-workflow/.github/workflows/OCV-PR-4.x-macOS-ARM64.yaml@main",
        # link: https://github.com/opencv/ci-gha-workflow/blob/main/.github/workflows/OCV-PR-4.x-macOS-ARM64.yaml, totally 6
        # has a taint source github.head_ref
    },{
        "type" : "e",
        "reusable_workflow" : "opencv/ci-gha-workflow/.github/workflows/OCV-PR-4.x-macOS-x86_64.yaml@main",
        # link: https://github.com/opencv/ci-gha-workflow/blob/main/.github/workflows/OCV-PR-4.x-macOS-x86_64.yaml, totally 6
        # has a taint source github.head_ref
    },{
        "type" : "e",
        "reusable_workflow" : "opencv/ci-gha-workflow/.github/workflows/OCV-PR-4.x-iOS.yaml@main",
        # link: https://github.com/opencv/ci-gha-workflow/blob/main/.github/workflows/OCV-PR-4.x-iOS.yaml, totally 2
        # has a taint source github.head_ref
    },{
        "type" : "e",
        "reusable_workflow" : "opencv/ci-gha-workflow/.github/workflows/OCV-timvx-backend-tests-4.x.yml@main",
        # link: https://github.com/opencv/ci-gha-workflow/blob/main/.github/workflows/OCV-timvx-backend-tests-4.x.yml, totally 5
        # has a taint source github.head_ref
    }],
    ObjectId('63dd962f045fe2c0b71640d3'): [{
        "type" : "e",
        "reusable_workflow" : "opencv/ci-gha-workflow/.github/workflows/OCV-PR-4.x-ARM64.yaml@main",
        # link: https://github.com/opencv/ci-gha-workflow/blob/main/.github/workflows/OCV-PR-4.x-ARM64.yaml, totally 6
        # has a taint source github.head_ref
    },{
        "type" : "e",
        "reusable_workflow" : "opencv/ci-gha-workflow/.github/workflows/OCV-PR-4.x-U20.yaml@main",
        # link: https://github.com/opencv/ci-gha-workflow/blob/main/.github/workflows/OCV-PR-4.x-U20.yaml, totally 6
        # has a taint source github.head_ref
    },{
        "type" : "e",
        "reusable_workflow" : "opencv/ci-gha-workflow/.github/workflows/OCV-PR-4.x-W10.yaml@main",
        # link: https://github.com/opencv/ci-gha-workflow/blob/main/.github/workflows/OCV-PR-4.x-W10.yaml, totally 6
        # has a taint source github.head_ref
    },{
        "type" : "e",
        "reusable_workflow" : "opencv/ci-gha-workflow/.github/workflows/OCV-PR-4.x-macOS-ARM64.yaml@main",
        # link: https://github.com/opencv/ci-gha-workflow/blob/main/.github/workflows/OCV-PR-4.x-macOS-ARM64.yaml, totally 6
        # has a taint source github.head_ref
    },{
        "type" : "e",
        "reusable_workflow" : "opencv/ci-gha-workflow/.github/workflows/OCV-PR-4.x-macOS-x86_64.yaml@main",
        # link: https://github.com/opencv/ci-gha-workflow/blob/main/.github/workflows/OCV-PR-4.x-macOS-x86_64.yaml, totally 6
        # has a taint source github.head_ref
    },{
        "type" : "e",
        "reusable_workflow" : "opencv/ci-gha-workflow/.github/workflows/OCV-PR-4.x-iOS.yaml@main",
        # link: https://github.com/opencv/ci-gha-workflow/blob/main/.github/workflows/OCV-PR-4.x-iOS.yaml, totally 2
        # has a taint source github.head_ref
    },{
        "type" : "e",
        "reusable_workflow" : "opencv/ci-gha-workflow/.github/workflows/OCV-timvx-backend-tests-4.x.yml@main",
        # link: https://github.com/opencv/ci-gha-workflow/blob/main/.github/workflows/OCV-timvx-backend-tests-4.x.yml, totally 5
        # has a taint source github.head_ref
    },{
        "type" : "e",
        "reusable_workflow" : "opencv/ci-gha-workflow/.github/workflows/OCV-PR-4.x-U20-Cuda.yaml@main",
        # link: https://github.com/opencv/ci-gha-workflow/blob/main/.github/workflows/OCV-PR-4.x-U20-Cuda.yaml, totally 4
        # has a taint source github.head_ref
    },{
        "type" : "e",
        "reusable_workflow" : "opencv/ci-gha-workflow/.github/workflows/OCV-PR-4.x-Android.yaml@main",
        # link: https://github.com/opencv/ci-gha-workflow/blob/main/.github/workflows/OCV-PR-4.x-Android.yaml, totally 2
        # has a taint source github.head_ref
    },{
        "type" : "e",
        "reusable_workflow" : "opencv/ci-gha-workflow/.github/workflows/OCV-PR-4.x-docs.yaml@main",
        # link: https://github.com/opencv/ci-gha-workflow/blob/main/.github/workflows/OCV-PR-4.x-docs.yaml, totally 4
        # has a taint source github.head_ref
    }],
    # ObjectId('63dd94a880aa29a6fd486c40'): false positive
    ObjectId('63dd963c80aa29a6fd4889af'): [{
        "type" : "e",
        "reusable_workflow" : "XNXKTech/workflows/.github/workflows/lark-notification.yml@main",
        # link: https://github.com/XNXKTech/workflows/blob/main/.github/workflows/lark-notification.yml
        # has taint sources:  github.event.head_commit.message, github.event.pull_request.title
    }],
    ObjectId('63dd957f045fe2c0b71638e1'): [{
        "type" : "e",
        "reusable_workflow" : "rest-for-physics/framework/.github/workflows/validation.yml@master",
        # link: https://github.com/rest-for-physics/framework/blob/master/.github/workflows/validation.yml, totally 6
        # has a taint source github.head_ref
    }],
    ObjectId('63dd96323c0647426a8cc094'): [{
        "type" : "e",
        "reusable_workflow" : "fmidev/.github/.github/workflows/helm-build-and-publish-to-github.yml@0.1.6",
        # link: https://github.com/fmidev/.github/blob/0.1.6/.github/workflows/helm-build-and-publish-to-github.yml, L68, L69
        # has taint sources: github.event.head_commit.author.email, github.event.head_commit.author.name
    },{
        "type" : "e",
        "reusable_workflow" : "fmidev/.github/.github/workflows/update-openshift-application-version.yml@0.1.6",
        # link: https://github.com/fmidev/.github/blob/0.1.6/.github/workflows/update-openshift-application-version.yml, L61, L62
        # has taint sources: github.event.head_commit.author.email, github.event.head_commit.author.name
    }],
    ObjectId('63dd962f80aa29a6fd488906'): [{
        "type" : "e",
        "reusable_workflow" : "pbs/pycaption/.github/workflows/main.yml@main",
        # link: https://github.com/pbs/pycaption/blob/5a914998d37ebe55d5dd93830e49284731686950/.github/workflows/main.yml#L52
        # has a taint source: github.head_ref
    }],
    ObjectId('63dd94c93c0647426a8ca85c'): [{
        "type" : "e",
        "reusable_workflow" : "rest-for-physics/framework/.github/workflows/validation.yml@master",
        # link: https://github.com/rest-for-physics/framework/blob/master/.github/workflows/validation.yml, totally 6
        # has a taint source github.head_ref
    }],
    ObjectId('63dd963480aa29a6fd488956'): [{
        "type" : "e",
        "reusable_workflow" : "WordPress/wordpress-develop/.github/workflows/slack-notifications.yml@trunk",
        # link: https://github.com/WordPress/wordpress-develop/blob/trunk/.github/workflows/slack-notifications.yml#L150
        # has a taint source github.event.head_commit.message
    }],
    ObjectId('63dd96553c0647426a8cc240'): [{
        "type" : "e",
        "reusable_workflow" : "mParticle/mparticle-workflows/.github/workflows/pr-branch-check-name.yml@main",
        # link: https://github.com/mParticle/mparticle-workflows/blob/main/.github/workflows/pr-branch-check-name.yml#L42
        # has a taint source github.event.pull_request.head.ref
    },{
        "type" : "e",
        "reusable_workflow" : "mParticle/mparticle-workflows/.github/workflows/pr-title-check.yml@main",
        # link: https://github.com/mParticle/mparticle-workflows/blob/main/.github/workflows/pr-title-check.yml#L41
        # has a taint source github.event.pull_request.title
    }],
    ObjectId('63dd96633c0647426a8cc340'): [{
        "type" : "e",
        "reusable_workflow" : "grafana/code-coverage/.github/workflows/code-coverage.yml@v0.1.12",
        # link: https://github.com/grafana/code-coverage/blob/v0.1.12/.github/workflows/code-coverage.yml, totally 2
        # has a taint source github.event.pull_request.head.ref
    }],
    ObjectId('63dd96353c0647426a8cc0a6'): [{
        "type" : "e",
        "reusable_workflow" : "WordPress/wordpress-develop/.github/workflows/slack-notifications.yml@trunk",
        # link: https://github.com/WordPress/wordpress-develop/blob/trunk/.github/workflows/slack-notifications.yml#L150
        # has a taint source github.event.head_commit.message
    }],
    ObjectId('63dd966380aa29a6fd488bf0'): [{
        "type" : "e",
        "reusable_workflow" : "grafana/code-coverage/.github/workflows/code-coverage.yml@v0.1.12",
        # link: https://github.com/grafana/code-coverage/blob/v0.1.12/.github/workflows/code-coverage.yml, totally 2
        # has a taint source github.event.pull_request.head.ref
    }],
    ObjectId('63dd962480aa29a6fd488896'): [{
        "type" : "e",
        "reusable_workflow" : "iotaledger/identity.rs/.github/workflows/shared-release.yml@main",
        # link: https://github.com/iotaledger/identity.rs/blob/main/.github/workflows/shared-release.yml#L73
        # has a taint source github.head_ref
    }],
    ObjectId('63dd96503c0647426a8cc1e9'): [{
        "type" : "e",
        "reusable_workflow" : "rajbos/github-actions-requests/.github/workflows/get-action-from-issue.yml@main",
        # link: https://github.com/rajbos/github-actions-requests/blob/main/.github/workflows/get-action-from-issue.yml#L51
        # has a taint source github.event.issue.title
    }],
    # ObjectId('63dd9511045fe2c0b7162fff'): false positive
    ObjectId('63dd962d80aa29a6fd4888ee'): [{
        "type" : "e",
        "reusable_workflow" : "rajbos/github-actions-requests/.github/workflows/get-action-from-issue.yml@main",
        # link: https://github.com/rajbos/github-actions-requests/blob/main/.github/workflows/get-action-from-issue.yml#L51
        # has a taint source github.event.issue.title
    }],
    ObjectId('63dd9626045fe2c0b716408c'): [{
        "type" : "e",
        "reusable_workflow" : "rajbos/github-actions-requests/.github/workflows/get-action-from-issue.yml@main",
        # link: https://github.com/rajbos/github-actions-requests/blob/main/.github/workflows/get-action-from-issue.yml#L51
        # has a taint source github.event.issue.title
    }],
    ObjectId('63dd96353c0647426a8cc0a7'): [{
        "type" : "e",
        "reusable_workflow" : "WordPress/wordpress-develop/.github/workflows/slack-notifications.yml@trunk",
        # link: https://github.com/WordPress/wordpress-develop/blob/trunk/.github/workflows/slack-notifications.yml#L150
        # has a taint source github.event.head_commit.message
    }],
    ObjectId('63dd96303c0647426a8cc06c'): [{
        "type" : "e",
        "reusable_workflow" : "pahrens-github/github-actions-requests/.github/workflows/get-action-from-issue.yml@main",
        # link: https://github.com/pahrens-github/github-actions-requests/blob/main/.github/workflows/get-action-from-issue.yml#L51
        # has a taint source github.event.issue.title
    }],
    # ObjectId('63dd966380aa29a6fd488bfa'): false positive
    ObjectId('63dd962e80aa29a6fd4888f8'): [{
        "type" : "e",
        "reusable_workflow" : "mParticle/mparticle-workflows/.github/workflows/pr-branch-check-name.yml@stable"
        # link: https://github.com/mParticle/mparticle-workflows/blob/stable/.github/workflows/pr-branch-check-name.yml#L42
        # has a taint source github.event.pull_request.head.ref
    },{
        "type" : "e",
        "reusable_workflow" : "mParticle/mparticle-workflows/.github/workflows/pr-title-check.yml@stable"
        # link: https://github.com/mParticle/mparticle-workflows/blob/stable/.github/workflows/pr-title-check.yml#L41
        # has a taint source github.event.pull_request.title
    }]
}

hardcoded_wrong_type_400 = {
    ObjectId('63dd962080aa29a6fd48886e'): [{
        "type" : "e",
        "reusable_workflow" : "openhie/empty-fhir-ig/.github/workflows/main.yml@master",
        # link: https://github.com/openhie/empty-fhir-ig/blob/master/.github/workflows/main.yml#L87
        # uses direct flow composite action tj-actions/branch-names@v4.3
    }],
    ObjectId('63dd96123c0647426a8cbf6f'): [{
        "type" : "b",
        "action" : "APN-Pucky/fast-forward-action@main",
        "action_type" : "composite_action",
        # link: https://github.com/APN-Pucky/fast-forward-action/blob/main/action.yml#L20
        # uses direct flow composite action APN-Pucky/fast-forward-action/label@main
    }],
    ObjectId('63dd96323c0647426a8cc094'): [{
        "type" : "e",
        "reusable_workflow" : "fmidev/.github/.github/workflows/docker-build-and-push.yml@0.1.6",
        # link: https://github.com/fmidev/.github/blob/0.1.6/.github/workflows/docker-build-and-push.yml#L67
        # uses direct flow composite action rlespinasse/github-slug-action@v4
    }],
    ObjectId('63dd9627045fe2c0b7164099'): [{
        "type" : "e",
        "reusable_workflow" : "rstudio/education-workflows/.github/workflows/auto-pkg-maintenance.yaml@v1",
        # link: https://github.com/rstudio/education-workflows/blob/v1/.github/workflows/auto-pkg-maintenance.yaml#L172
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd963680aa29a6fd488977'): [{
        "type" : "e",
        "reusable_workflow" : "rstudio/shiny-workflows/.github/workflows/routine.yaml@v1",
        # link: https://github.com/rstudio/shiny-workflows/blob/v1/.github/workflows/routine.yaml#L176
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd961c80aa29a6fd488856'): [{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/style.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/style.yml#L39
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/spellcheck.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/spellcheck.yml
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/readme-render.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/readme-render.yml
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/pkgdown.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/pkgdown.yml
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/code-coverage.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/code-coverage.yml
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/man-pages.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/man-pages.yml
        # uses direct flow composite action tj-actions/branch-names@v5.4
    }],
    ObjectId('63dd960f045fe2c0b7163fbc'): [{
        "type" : "b",
        "action" : "smartlyio/github-actions@release-action-node-v1",
        "action_type" : "composite_action",
        # link: https://github.com/smartlyio/github-actions/blob/release-action-node-v1/release-action-node/action.yml
        # uses direct flow composite action smartlyio/github-actions@check-branch-behind-v1
    }],
    ObjectId('63dd95eb80aa29a6fd48863b'): [{
        "type" : "b",
        "action" : "APN-Pucky/fast-forward-action@main", 
        "action_type" : "composite_action",
        # link: https://github.com/APN-Pucky/fast-forward-action/blob/main/action.yml#L20
        # uses direct flow composite action APN-Pucky/fast-forward-action/label@main
    }],
    ObjectId('63dd96473c0647426a8cc16d'): [{
        "type" : "e",
        "reusable_workflow" : "rstudio/shiny-workflows/.github/workflows/routine.yaml@v1",
        # link: https://github.com/rstudio/shiny-workflows/blob/v1/.github/workflows/routine.yaml#L176
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd95e480aa29a6fd4885e5'): [{
        "type" : "b",
        "action" : "smartlyio/github-actions@release-action-node-v1",
        "action_type" : "composite_action",
        # link: https://github.com/smartlyio/github-actions/blob/release-action-node-v1/release-action-node/action.yml
        # uses direct flow composite action smartlyio/github-actions@check-branch-behind-v1
    }],
    ObjectId('63dd964580aa29a6fd488a0f'):[{
        "type" : "e",
        "reusable_workflow" : "rstudio/shiny-workflows/.github/workflows/routine.yaml@v1",
        # link: https://github.com/rstudio/shiny-workflows/blob/v1/.github/workflows/routine.yaml#L176
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd9621045fe2c0b7164057'): [{
        "type" : "e",
        "reusable_workflow" : "blockscout/blockscout-ci-cd/.github/workflows/e2e_new.yaml@master",
        # link: https://github.com/blockscout/blockscout-ci-cd/blob/master/.github/workflows/e2e_new.yaml
        # uses direct flow composite action rlespinasse/github-slug-action@v4
    }],
    ObjectId('63dd961a3c0647426a8cbfac'): [{
        "type" : "b",
        "action" : "sfeir-open-source/sfeir-school-github-action-dev/.github/actions/runs-using-composite@main",
        "action_type" : "composite_action",
        # link: https://github.com/sfeir-open-source/sfeir-school-github-action-dev/blob/main/.github/actions/runs-using-composite/action.yaml
        # uses direct flow composite action rlespinasse/github-slug-action@v4
    }],
    ObjectId('63dd961b3c0647426a8cbfb6'):[{
        "type" : "e",
        "reusable_workflow" : "openhie/empty-fhir-ig/.github/workflows/main.yml@master",
        # link: https://github.com/openhie/empty-fhir-ig/blob/master/.github/workflows/main.yml
        # uses direct flow composite action tj-actions/branch-names@v4.3
    }],
    ObjectId('63dd9613045fe2c0b7163fe8'):[{
        "type" : "b",
        "action" : "CleverShuttle/gh-composite-actions/actions/rebase-nonprod@v1",
        "action_type" : "composite_action",
        # link: not found
        # uses direct flow composite action tj-actions/branch-names@v6 and has a vulnerable script
    }],
    ObjectId('63dd962180aa29a6fd488873'):[{
        "type" : "e",
        "reusable_workflow" : "k8s-at-home/charts/.github/workflows/pr-metadata.yaml@master",
        # link: https://github.com/k8s-at-home/charts/blob/master/.github/workflows/pr-metadata.yaml
        # uses direct flow composite action tj-actions/branch-names@v5.4
    }],
    ObjectId('63dd96313c0647426a8cc085'):[{
        "type" : "e",
        "reusable_workflow" : "rstudio/shiny-workflows/.github/workflows/routine.yaml@v1",
        # link: https://github.com/rstudio/shiny-workflows/blob/v1/.github/workflows/routine.yaml#L176
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd95e180aa29a6fd4885bf'):[{
        "type" : "b",
        "action" : "CumulusDS/workflow-setup-action@v1",
        "action_type" : "composite_action",
        # link: not found
        # uses direct flow composite action CumulusDS/feature-stage-action@v1
    }],
    ObjectId('63dd95b9045fe2c0b7163bd0'): [{
        "type" : "b",
        "action" : "smartlyio/github-actions@release-action-node-v1",
        "action_type" : "composite_action",
        # link: https://github.com/smartlyio/github-actions/blob/release-action-node-v1/release-action-node/action.yml
        # uses direct flow composite action smartlyio/github-actions@check-branch-behind-v1
    }],
    ObjectId('63dd95cf045fe2c0b7163cba'): [{
        "type" : "b",
        "action" : "team-gsri/actions-arma-tools/release-mission@v0",
        "action_type" : "composite_action",
        # link: https://github.com/team-gsri/actions-arma-tools/blob/v0/release-mission/action.yml
        # uses direct flow composite action arwynfr/actions-conventional-versioning/get-newVersion@v1 and arwynfr/actions-conventional-versioning@v1
    }],
    ObjectId('63dd961f3c0647426a8cbfd3'): [{
        "type" : "e",
        "reusable_workflow" : "openhie/empty-fhir-ig/.github/workflows/main.yml@master",
        # link: https://github.com/openhie/empty-fhir-ig/blob/master/.github/workflows/main.yml#L87
        # uses direct flow composite action tj-actions/branch-names@v4.3
    }],
    ObjectId('63dd961e045fe2c0b7164048'): [{
        "type" : "e",
        "reusable_workflow" : "erzz/workflows/.github/workflows/semantic-release.yml@main",
        # link: https://github.com/erzz/workflows/blob/main/.github/workflows/semantic-release.yml#L98
        # uses direct flow composite action rlespinasse/github-slug-action@4.2.4
    }],
    ObjectId('63dd95f83c0647426a8cbe4f'): [{
        "type" : "b",
        "action" : "APN-Pucky/fast-forward-action@main",
        "action_type" : "composite_action",
        # link: https://github.com/APN-Pucky/fast-forward-action/blob/main/action.yml#L20
        # uses direct flow composite action APN-Pucky/fast-forward-action/label@main
    }],
    ObjectId('63dd95653c0647426a8cb6ca'):  [{
        "type" : "b",
        "action" : "insightsengineering/coverage-action@v2.1.2",
        "action_type" : "composite_action",
        # link: https://github.com/insightsengineering/coverage-action/blob/v2.1.2/action.yml#L72
        # uses direct flow composite action tj-actions/branch-names@v5.1
    }],
    ObjectId('63dd964280aa29a6fd4889ed'): [{
        "type" : "e",
        "reusable_workflow" : "rstudio/education-workflows/.github/workflows/auto-pkg-maintenance.yaml@v1",
        # link: https://github.com/rstudio/education-workflows/blob/v1/.github/workflows/auto-pkg-maintenance.yaml#L172
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd963b3c0647426a8cc100'): [{
        "type" : "e",
        "reusable_workflow" : "rstudio/education-workflows/.github/workflows/auto-pkg-maintenance.yaml@v1",
        # link: https://github.com/rstudio/education-workflows/blob/v1/.github/workflows/auto-pkg-maintenance.yaml#L172
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd961c80aa29a6fd488858'): [{
        "type" : "e",
        "reusable_workflow" : "erzz/workflows/.github/workflows/semantic-release.yml@main",
        # link: https://github.com/erzz/workflows/blob/main/.github/workflows/semantic-release.yml#L98
        # uses direct flow composite action rlespinasse/github-slug-action@4.2.4
    }],
    ObjectId('63dd96203c0647426a8cbfde'): [{
        "type" : "e",
        "reusable_workflow" : "onedr0p/containers/.github/workflows/pr-metadata.yaml@main",
        # link: https://github.com/onedr0p/containers/blob/56573df014aea7cdc0cd058590b1ba93f5a22e7b/.github/workflows/pr-metadata.yaml#L30
        # uses direct flow composite action tj-actions/branch-names@v6.2
    }],
    ObjectId('63dd963080aa29a6fd488919'): [{
        "type" : "e",
        "reusable_workflow" : "rstudio/shiny-workflows/.github/workflows/routine.yaml@v1",
        # link: https://github.com/rstudio/shiny-workflows/blob/v1/.github/workflows/routine.yaml#L176
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd9626045fe2c0b7164083'): [{
        "type" : "e",
        "reusable_workflow" : "rstudio/shiny-workflows/.github/workflows/routine.yaml@v1",
        # link: https://github.com/rstudio/shiny-workflows/blob/v1/.github/workflows/routine.yaml#L176
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd95d93c0647426a8cbcd0'): [{
        "type" : "b",
        "action" : "smartlyio/github-actions@release-action-node-v1",
        "action_type" : "composite_action",
        # link: https://github.com/smartlyio/github-actions/blob/release-action-node-v1/release-action-node/action.yml
        # uses direct flow composite action smartlyio/github-actions@check-branch-behind-v1
    }],
    ObjectId('63dd962a80aa29a6fd4888c5'): [{
        "type" : "e",
        "reusable_workflow" : "rstudio/shiny-workflows/.github/workflows/routine.yaml@v1",
        # link: https://github.com/rstudio/shiny-workflows/blob/v1/.github/workflows/routine.yaml#L176
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd95d080aa29a6fd4884f8'): [{
        "type" : "b",
        "action" : "smartlyio/github-actions@release-action-node-v1",
        "action_type" : "composite_action",
        # link: https://github.com/smartlyio/github-actions/blob/release-action-node-v1/release-action-node/action.yml
        # uses direct flow composite action smartlyio/github-actions@check-branch-behind-v1
    }],
    ObjectId('63dd961b045fe2c0b716402f'): [{
        "type" : "e",
        "reusable_workflow" : "openhie/empty-fhir-ig/.github/workflows/main.yml@master",
        # link: https://github.com/openhie/empty-fhir-ig/blob/master/.github/workflows/main.yml#L87
        # uses direct flow composite action tj-actions/branch-names@v4.3
    }],
    ObjectId('63dd95e480aa29a6fd4885e4'): [{
        "type" : "b",
        "action" : "smartlyio/github-actions@release-action-node-v1",
        "action_type" : "composite_action",
        # link: https://github.com/smartlyio/github-actions/blob/release-action-node-v1/release-action-node/action.yml
        # uses direct flow composite action smartlyio/github-actions@check-branch-behind-v1
    }],
    ObjectId('63dd95c13c0647426a8cbbc8'): [{
        "type" : "b",
        "action" : "PiwikPRO/actions/go/test@master",
        "action_type" : "composite_action",
        # link: https://github.com/PiwikPRO/actions/blob/master/go/test/action.yaml#L86        
        # uses direct flow composite action PiwikPRO/actions/coverage@master
    }],
    ObjectId('63dd96213c0647426a8cbfe7'): [{
        "type" : "e",
        "reusable_workflow" : "k8s-at-home/charts/.github/workflows/pr-metadata.yaml@master",
        # link: https://github.com/k8s-at-home/charts/blob/master/.github/workflows/pr-metadata.yaml
        # uses direct flow composite action tj-actions/branch-names@v5.4
    }],
    ObjectId('63dd961c3c0647426a8cbfc2'): [{
        "type" : "e",
        "reusable_workflow" : "cloud-tek/hive/.github/workflows/nuke.yml@main",
        # link: https://github.com/cloud-tek/hive/blob/main/.github/workflows/nuke.yml#L85
        # uses direct flow composite action cloud-tek/actions/auto-release@0.19
    }],
    ObjectId('63dd963680aa29a6fd488974'): [{
        "type" : "e",
        "reusable_workflow" : "rstudio/shiny-workflows/.github/workflows/routine.yaml@v1",
        # link: https://github.com/rstudio/shiny-workflows/blob/v1/.github/workflows/routine.yaml#L176
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd961b045fe2c0b7164033'):  [{
        "type" : "e",
        "reusable_workflow" : "openhie/empty-fhir-ig/.github/workflows/main.yml@master",
        # link: https://github.com/openhie/empty-fhir-ig/blob/master/.github/workflows/main.yml#L87
        # uses direct flow composite action tj-actions/branch-names@v4.3
    }],
    ObjectId('63dd961b80aa29a6fd488854'): [{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/style.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/style.yml#L39
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/spellcheck.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/spellcheck.yml#L51
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/readme-render.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/readme-render.yml#L45
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/pkgdown.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/pkgdown.yml#L92
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/lintr.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/lintr.yml#L70
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/code-coverage.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/code-coverage.yml#L52
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/man-pages.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/man-pages.yml#L40
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/r-pkg-validation.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/r-pkg-validation.yml#L42
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/check-templates.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/check-templates.yml#L41
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/r-cmd-check.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/f3e3800d15e94ebbe2aafb07bd3c8e06dae638a5/.github/workflows/r-cmd-check.yml#L51
        # uses direct flow composite action tj-actions/branch-names@v5.4
    }],
    ObjectId('63dd962280aa29a6fd488884'): [{
        "type" : "e",
        "reusable_workflow" : "rstudio/shiny-workflows/.github/workflows/routine.yaml@v1",
        # link: https://github.com/rstudio/shiny-workflows/blob/v1/.github/workflows/routine.yaml#L176
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd9631045fe2c0b71640ec'): [{
        "type" : "e",
        "reusable_workflow" : "rstudio/education-workflows/.github/workflows/auto-pkg-maintenance.yaml@v1",
        # link: https://github.com/rstudio/education-workflows/blob/v1/.github/workflows/auto-pkg-maintenance.yaml#L172
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd964f045fe2c0b7164209'): [{
        "type" : "e",
        "reusable_workflow" : "rstudio/shiny-workflows/.github/workflows/routine.yaml@v1",
        # link: https://github.com/rstudio/shiny-workflows/blob/v1/.github/workflows/routine.yaml#L176
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd963980aa29a6fd488994'): [{
        "type" : "e",
        "reusable_workflow" : "rstudio/shiny-workflows/.github/workflows/routine.yaml@v1",
        # link: https://github.com/rstudio/shiny-workflows/blob/v1/.github/workflows/routine.yaml#L176
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd961f80aa29a6fd488869'): [{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/style.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/style.yml#L39
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/spellcheck.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/spellcheck.yml#L51
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/readme-render.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/readme-render.yml#L45
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/pkgdown.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/pkgdown.yml#L92
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/lintr.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/lintr.yml#L70
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/code-coverage.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/code-coverage.yml#L52
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/man-pages.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/man-pages.yml#L40
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/r-pkg-validation.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/r-pkg-validation.yml#L42
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/r-cmd-check.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/f3e3800d15e94ebbe2aafb07bd3c8e06dae638a5/.github/workflows/r-cmd-check.yml#L51
        # uses direct flow composite action tj-actions/branch-names@v5.4
    }],
    ObjectId('63dd95f780aa29a6fd4886cd'): [{
        "type" : "b",
        "action" : "smartlyio/github-actions@release-action-node-v1",
        "action_type" : "composite_action",
        # link: https://github.com/smartlyio/github-actions/blob/release-action-node-v1/release-action-node/action.yml
        # uses direct flow composite action smartlyio/github-actions@check-branch-behind-v1
    }],
    ObjectId('63dd960f3c0647426a8cbf4d'): [{
        "type" : "b",
        "action" : "smartlyio/github-actions@release-action-node-v1",
        "action_type" : "composite_action",
        # link: https://github.com/smartlyio/github-actions/blob/release-action-node-v1/release-action-node/action.yml
        # uses direct flow composite action smartlyio/github-actions@check-branch-behind-v1
    }],
    ObjectId('63dd95c8045fe2c0b7163c6d'): [{
        "type" : "b",
        "action" : "smartlyio/github-actions@release-action-node-v1",
        "action_type" : "composite_action",
        # link: https://github.com/smartlyio/github-actions/blob/release-action-node-v1/release-action-node/action.yml
        # uses direct flow composite action smartlyio/github-actions@check-branch-behind-v1
    }],
    ObjectId('63dd95dd80aa29a6fd488593'): [{
        "type" : "b",
        "action" : "smartlyio/github-actions@release-action-node-v1",
        "action_type" : "composite_action",
        # link: https://github.com/smartlyio/github-actions/blob/release-action-node-v1/release-action-node/action.yml
        # uses direct flow composite action smartlyio/github-actions@check-branch-behind-v1
    }],
    ObjectId('63dd95ef3c0647426a8cbdf0'): [{
        "type" : "b",
        "action" : "smartlyio/github-actions@release-action-node-v1",
        "action_type" : "composite_action",
        # link: https://github.com/smartlyio/github-actions/blob/release-action-node-v1/release-action-node/action.yml
        # uses direct flow composite action smartlyio/github-actions@check-branch-behind-v1
    }],
    ObjectId('63dd9602045fe2c0b7163f31'): [{
        "type" : "b",
        "action" : "team-gsri/actions-arma-tools/release-mod@v0",
        "action_type" : "composite_action",
        # link: https://github.com/team-gsri/actions-arma-tools/blob/v0/release-mod/action.yml
        # uses direct flow composite action arwynfr/actions-conventional-versioning/get-newVersion@v1 and arwynfr/actions-conventional-versioning@v1
    }],
    ObjectId('63dd95f780aa29a6fd4886cc'): [{
        "type" : "b",
        "action" : "smartlyio/github-actions@release-action-node-v1",
        "action_type" : "composite_action",
        # link: https://github.com/smartlyio/github-actions/blob/release-action-node-v1/release-action-node/action.yml
        # uses direct flow composite action smartlyio/github-actions@check-branch-behind-v1
    }],
    ObjectId('63dd95d93c0647426a8cbccf'): [{
        "type" : "b",
        "action" : "smartlyio/github-actions@release-action-node-v1",
        "action_type" : "composite_action",
        # link: https://github.com/smartlyio/github-actions/blob/release-action-node-v1/release-action-node/action.yml
        # uses direct flow composite action smartlyio/github-actions@check-branch-behind-v1
    }],
    ObjectId('63dd95de3c0647426a8cbd12'): [{
        "type" : "b",
        "action" : "fabriziocacicia/keep-history-conventional@v0.1.0",
        "action_type" : "composite_action",
        # link: https://github.com/fabriziocacicia/keep-history-conventional/blob/v0.1.0/action.yml#L25
        # uses composite action fabriziocacicia/move-latest-commit-to-pr-action@v0.3.0
        # link: https://github.com/fabriziocacicia/move-latest-commit-to-pr-action/blob/8c6386a7f3173ff6e665d4f88ce676ceb0e36fa8/action.yml#L31
        # action fabriziocacicia/move-latest-commit-to-pr-action@v0.3.0 uses direct flow composite action tj-actions/branch-names@v5.2
    }],
    ObjectId('63dd9626045fe2c0b7164082'): [{
        "type" : "e",
        "reusable_workflow" : "rstudio/shiny-workflows/.github/workflows/routine.yaml@v1",
        # link: https://github.com/rstudio/shiny-workflows/blob/v1/.github/workflows/routine.yaml#L176
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd963180aa29a6fd488921'): [{
        "type" : "e",
        "reusable_workflow" : "rstudio/shiny-workflows/.github/workflows/routine.yaml@v1",
        # link: https://github.com/rstudio/shiny-workflows/blob/v1/.github/workflows/routine.yaml#L176
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd95fd3c0647426a8cbe91'): [{
        "type" : "b",
        "action" : "team-gsri/actions-arma-tools/release-mod@v0",
        "action_type" : "composite_action",
        # link: https://github.com/team-gsri/actions-arma-tools/blob/v0/release-mod/action.yml
        # uses direct flow composite action arwynfr/actions-conventional-versioning/get-newVersion@v1 and arwynfr/actions-conventional-versioning@v1
    }],
    ObjectId('63dd962280aa29a6fd48887b'): [{
        "type" : "e",
        "reusable_workflow" : "akarthik10/charts/.github/workflows/pr-metadata.yaml@master",
        # link: https://github.com/akarthik10/charts/blob/2ea4019827ea12edc81d16125d869fb156c917a2/.github/workflows/pr-metadata.yaml#L32
        # uses direct flow composite action tj-actions/branch-names@v6.2
    }],
    ObjectId('63dd963980aa29a6fd488993'): [{
        "type" : "e",
        "reusable_workflow" : "rstudio/shiny-workflows/.github/workflows/routine.yaml@v1",
        # link: https://github.com/rstudio/shiny-workflows/blob/v1/.github/workflows/routine.yaml#L176
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd95e13c0647426a8cbd36'): [{
        "type" : "b",
        "action" : "jahia/jahia-modules-action/slack-jahia@v2",
        "action_type" : "composite_action",
        # link: https://github.com/Jahia/jahia-modules-action/blob/v2/slack-jahia/action.yml#L35
        # uses direct flow composite action tj-actions/branch-names@v6
    }],
    ObjectId('63dd964080aa29a6fd4889dd'): [{
        "type" : "e",
        "reusable_workflow" : "rstudio/shiny-workflows/.github/workflows/routine.yaml@v1",
        # link: https://github.com/rstudio/shiny-workflows/blob/v1/.github/workflows/routine.yaml#L176
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd962a045fe2c0b71640b0'): [{
        "type" : "e",
        "reusable_workflow" : "rstudio/shiny-workflows/.github/workflows/routine.yaml@v1",
        # link: https://github.com/rstudio/shiny-workflows/blob/v1/.github/workflows/routine.yaml#L176
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd961f045fe2c0b716404c'): [{
        "type" : "e",
        "reusable_workflow" : "openhie/empty-fhir-ig/.github/workflows/main.yml@master",
        # link: https://github.com/openhie/empty-fhir-ig/blob/master/.github/workflows/main.yml#L87
        # uses direct flow composite action tj-actions/branch-names@v4.3
    }],
    ObjectId('63dd96243c0647426a8cc000'): [{
        "type" : "e",
        "reusable_workflow" : "rstudio/shiny-workflows/.github/workflows/routine.yaml@v1",
        # link: https://github.com/rstudio/shiny-workflows/blob/v1/.github/workflows/routine.yaml#L176
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd95c380aa29a6fd488459'): [{
        "type" : "b",
        "action" : "smartlyio/github-actions@release-action-node-v1",
        "action_type" : "composite_action",
        # link: https://github.com/smartlyio/github-actions/blob/release-action-node-v1/release-action-node/action.yml
        # uses direct flow composite action smartlyio/github-actions@check-branch-behind-v1
    }],
    ObjectId('63dd95ef045fe2c0b7163e4a'): [{
        "type" : "b",
        "action" : "smartlyio/github-actions@release-action-node-v1",
        "action_type" : "composite_action",
        # link: https://github.com/smartlyio/github-actions/blob/release-action-node-v1/release-action-node/action.yml
        # uses direct flow composite action smartlyio/github-actions@check-branch-behind-v1
    }],
    ObjectId('63dd962180aa29a6fd488871'): [{
        "type" : "e",
        "reusable_workflow" : "k8s-at-home/charts/.github/workflows/pr-metadata.yaml@master",
        # link: https://github.com/k8s-at-home/charts/blob/master/.github/workflows/pr-metadata.yaml
        # uses direct flow composite action tj-actions/branch-names@v5.4
    }],
    ObjectId('63dd9640045fe2c0b716416b'): [{
        "type" : "e",
        "reusable_workflow" : "rstudio/shiny-workflows/.github/workflows/routine.yaml@v1",
        # link: https://github.com/rstudio/shiny-workflows/blob/v1/.github/workflows/routine.yaml#L176
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd962e045fe2c0b71640ca'): [{
        "type" : "e",
        "reusable_workflow" : "rstudio/shiny-workflows/.github/workflows/routine.yaml@v1",
        # link: https://github.com/rstudio/shiny-workflows/blob/v1/.github/workflows/routine.yaml#L176
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd961c3c0647426a8cbfc3'): [{
        "type" : "e",
        "reusable_workflow" : "openhie/empty-fhir-ig/.github/workflows/main.yml@master",
        # link: https://github.com/openhie/empty-fhir-ig/blob/master/.github/workflows/main.yml#L87
        # uses direct flow composite action tj-actions/branch-names@v4.3
    }],
    ObjectId('63dd964d045fe2c0b71641ee'): [{
        "type" : "e",
        "reusable_workflow" : "rstudio/shiny-workflows/.github/workflows/routine.yaml@v1",
        # link: https://github.com/rstudio/shiny-workflows/blob/v1/.github/workflows/routine.yaml#L176
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd961f3c0647426a8cbfd6'): [{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/style.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/style.yml#L39
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/spellcheck.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/spellcheck.yml#L51
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/readme-render.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/readme-render.yml#L45
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/pkgdown.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/pkgdown.yml#L92
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/lintr.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/lintr.yml#L70
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/code-coverage.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/code-coverage.yml#L52
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/man-pages.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/man-pages.yml#L40
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/r-pkg-validation.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/r-pkg-validation.yml#L42
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/r-cmd-check.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/f3e3800d15e94ebbe2aafb07bd3c8e06dae638a5/.github/workflows/r-cmd-check.yml#L51
        # uses direct flow composite action tj-actions/branch-names@v5.4
    }],
    ObjectId('63dd95ce80aa29a6fd4884e3'): [{
        "type" : "b",
        "action" : "smartlyio/github-actions@release-action-node-v1",
        "action_type" : "composite_action",
        # link: https://github.com/smartlyio/github-actions/blob/release-action-node-v1/release-action-node/action.yml
        # uses direct flow composite action smartlyio/github-actions@check-branch-behind-v1
    }],
    ObjectId('63dd96203c0647426a8cbfe0'): [{
        "type" : "e",
        "reusable_workflow" : "blockscout/blockscout-ci-cd/.github/workflows/e2e_new.yaml@master",
        # link: https://github.com/blockscout/blockscout-ci-cd/blob/master/.github/workflows/e2e_new.yaml
        # uses direct flow composite action rlespinasse/github-slug-action@v4
    }],
    ObjectId('63dd9647045fe2c0b71641af'): [{
        "type" : "e",
        "reusable_workflow" : "rstudio/shiny-workflows/.github/workflows/routine.yaml@v1",
        # link: https://github.com/rstudio/shiny-workflows/blob/v1/.github/workflows/routine.yaml#L176
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd95c380aa29a6fd48845a'): [{
        "type" : "b",
        "action" : "smartlyio/github-actions@release-action-node-v1",
        "action_type" : "composite_action",
        # link: https://github.com/smartlyio/github-actions/blob/release-action-node-v1/release-action-node/action.yml
        # uses direct flow composite action smartlyio/github-actions@check-branch-behind-v1
    }],
    ObjectId('63dd96313c0647426a8cc07c'): [{
        "type" : "e",
        "reusable_workflow" : "rstudio/shiny-workflows/.github/workflows/routine.yaml@v1",
        # link: https://github.com/rstudio/shiny-workflows/blob/v1/.github/workflows/routine.yaml#L176
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd962f3c0647426a8cc05e'): [{
        "type" : "e",
        "reusable_workflow" : "rstudio/shiny-workflows/.github/workflows/routine.yaml@v1",
        # link: https://github.com/rstudio/shiny-workflows/blob/v1/.github/workflows/routine.yaml#L176
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd9648045fe2c0b71641ba'): [{
        "type" : "e",
        "reusable_workflow" : "rstudio/shiny-workflows/.github/workflows/routine.yaml@v1",
        # link: https://github.com/rstudio/shiny-workflows/blob/v1/.github/workflows/routine.yaml#L176
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd95fb045fe2c0b7163ee3'): [{
        "type" : "b",
        "action" : "insightsengineering/coverage-action@v2",
        "action_type" : "composite_action",
        # link: https://github.com/insightsengineering/coverage-action/blob/v2/action.yml#L84
        # uses direct flow composite action tj-actions/branch-names@v6.3
    }],
    ObjectId('63dd9641045fe2c0b7164179'): [{
        "type" : "e",
        "reusable_workflow" : "rstudio/shiny-workflows/.github/workflows/routine.yaml@v1",
        # link: https://github.com/rstudio/shiny-workflows/blob/v1/.github/workflows/routine.yaml#L176
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd962d80aa29a6fd4888e6'): [{
        "type" : "e",
        "reusable_workflow" : "rstudio/shiny-workflows/.github/workflows/routine.yaml@v1",
        # link: https://github.com/rstudio/shiny-workflows/blob/v1/.github/workflows/routine.yaml#L176
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd961b3c0647426a8cbfb7'): [{
        "type" : "e",
        "reusable_workflow" : "bjw-s/container-images/.github/workflows/pr-metadata.yaml@main",
        # link: https://github.com/bjw-s/container-images/blob/0bc61afb6065f837d7e1cbe33b636cce0209670d/.github/workflows/pr-metadata.yaml#L30
        # uses direct flow composite action tj-actions/branch-names@v6.2
    }],
    ObjectId('63dd961d3c0647426a8cbfcc'): [{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/style.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/style.yml#L39
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/spellcheck.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/spellcheck.yml#L51
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/readme-render.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/readme-render.yml#L45
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/pkgdown.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/pkgdown.yml#L92
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/lintr.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/lintr.yml#L70
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/code-coverage.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/code-coverage.yml#L52
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/man-pages.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/man-pages.yml#L40
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/r-pkg-validation.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/r-pkg-validation.yml#L42
        # uses direct flow composite action tj-actions/branch-names@v5.4
    },{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/r-cmd-check.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/f3e3800d15e94ebbe2aafb07bd3c8e06dae638a5/.github/workflows/r-cmd-check.yml#L51
        # uses direct flow composite action tj-actions/branch-names@v5.4
    }],
    ObjectId('63dd95ce045fe2c0b7163cb0'): [{
        "type" : "b",
        "action" : "smartlyio/github-actions@release-action-node-v1",
        "action_type" : "composite_action",
        # link: https://github.com/smartlyio/github-actions/blob/release-action-node-v1/release-action-node/action.yml
        # uses direct flow composite action smartlyio/github-actions@check-branch-behind-v1
    }],
    ObjectId('63dd95df3c0647426a8cbd27'): [{
        "type" : "b",
        "action" : "team-gsri/actions-arma-tools/release-mission@v0",
        "action_type" : "composite_action",
        # link: https://github.com/team-gsri/actions-arma-tools/blob/v0/release-mission/action.yml
        # uses direct flow composite action arwynfr/actions-conventional-versioning/get-newVersion@v1 and arwynfr/actions-conventional-versioning@v1
    }],
    ObjectId('63dd961c045fe2c0b7164037'): [{
        "type" : "e",
        "reusable_workflow" : "openhie/empty-fhir-ig/.github/workflows/main.yml@master",
        # link: https://github.com/openhie/empty-fhir-ig/blob/master/.github/workflows/main.yml#L87
        # uses direct flow composite action tj-actions/branch-names@v4.3
    }],
    ObjectId('63dd95d8045fe2c0b7163d25'): [{
        "type" : "b",
        "action" : "smartlyio/github-actions@release-action-node-v1",
        "action_type" : "composite_action",
        # link: https://github.com/smartlyio/github-actions/blob/release-action-node-v1/release-action-node/action.yml
        # uses direct flow composite action smartlyio/github-actions@check-branch-behind-v1
    }],
    ObjectId('63dd962180aa29a6fd488875'): [{
        "type" : "e",
        "reusable_workflow" : "k8s-at-home/charts/.github/workflows/pr-metadata.yaml@master",
        # link: https://github.com/k8s-at-home/charts/blob/master/.github/workflows/pr-metadata.yaml
        # uses direct flow composite action tj-actions/branch-names@v5.4
    }],
    ObjectId('63dd964a3c0647426a8cc18b'): [{
        "type" : "e",
        "reusable_workflow" : "rstudio/shiny-workflows/.github/workflows/routine.yaml@v1",
        # link: https://github.com/rstudio/shiny-workflows/blob/v1/.github/workflows/routine.yaml#L176
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd95d83c0647426a8cbccd'): [{
        "type" : "b",
        "action" : "smartlyio/github-actions@release-action-node-v1",
        "action_type" : "composite_action",
        # link: https://github.com/smartlyio/github-actions/blob/release-action-node-v1/release-action-node/action.yml
        # uses direct flow composite action smartlyio/github-actions@check-branch-behind-v1
    }],
    ObjectId('63dd95fa80aa29a6fd4886f4'): [{
        "type" : "b",
        "action" : "smartlyio/github-actions@release-action-node-v1",
        "action_type" : "composite_action",
        # link: https://github.com/smartlyio/github-actions/blob/release-action-node-v1/release-action-node/action.yml
        # uses direct flow composite action smartlyio/github-actions@check-branch-behind-v1
    }],
    ObjectId('63dd95b93c0647426a8cbb83'): [{
        "type" : "b",
        "action" : "smartlyio/github-actions@release-action-node-v1",
        "action_type" : "composite_action",
        # link: https://github.com/smartlyio/github-actions/blob/release-action-node-v1/release-action-node/action.yml
        # uses direct flow composite action smartlyio/github-actions@check-branch-behind-v1
    }],
    ObjectId('63dd9622045fe2c0b716405f'): [{
        "type" : "e",
        "reusable_workflow" : "rstudio/shiny-workflows/.github/workflows/routine.yaml@v1",
        # link: https://github.com/rstudio/shiny-workflows/blob/v1/.github/workflows/routine.yaml#L176
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd961e80aa29a6fd488865'): [{
        "type" : "e",
        "reusable_workflow" : "erzz/workflows/.github/workflows/container.yml@main",
        # link: https://github.com/erzz/workflows/blob/main/.github/workflows/container.yml#L93
        # uses direct flow composite action rlespinasse/github-slug-action@v4
    },{
        "type" : "e",
        "reusable_workflow" : "erzz/workflows/.github/workflows/source-protection.yml@main",
        # link: https://github.com/erzz/workflows/blob/main/.github/workflows/source-protection.yml#L70
        # uses direct flow composite action rlespinasse/github-slug-action@v4
    },{
        "type" : "e",
        "reusable_workflow" : "erzz/workflows/.github/workflows/node-tests.yml@main",
        # link: https://github.com/erzz/workflows/blob/main/.github/workflows/node-tests.yml#L79
        # uses direct flow composite action rlespinasse/github-slug-action@v4
    },{
        "type" : "e",
        "reusable_workflow" : "erzz/workflows/.github/workflows/semantic-release.yml@main",
        # link: https://github.com/erzz/workflows/blob/main/.github/workflows/semantic-release.yml#L98
        # uses direct flow composite action rlespinasse/github-slug-action@4.2.4
    }],
    ObjectId('63dd95dd80aa29a6fd488592'):[{
        "type" : "b",
        "action" : "smartlyio/github-actions@release-action-node-v1",
        "action_type" : "composite_action",
        # link: https://github.com/smartlyio/github-actions/blob/release-action-node-v1/release-action-node/action.yml
        # uses direct flow composite action smartlyio/github-actions@check-branch-behind-v1
    }],
    ObjectId('63dd961b045fe2c0b7164030'):[{
        "type" : "e",
        "reusable_workflow" : "cloud-tek/build/.github/workflows/dotnet.yml@main",
        # link: https://github.com/cloud-tek/build/blob/main/.github/workflows/dotnet.yml#L81
        # uses direct flow composite action cloud-tek/actions/auto-release@0.12
    }],
    ObjectId('63dd9627045fe2c0b7164093'): [{
        "type" : "e",
        "reusable_workflow" : "rstudio/shiny-workflows/.github/workflows/routine.yaml@v1",
        # link: https://github.com/rstudio/shiny-workflows/blob/v1/.github/workflows/routine.yaml#L176
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd961c80aa29a6fd488857'): [{
        "type" : "e",
        "reusable_workflow" : "openhie/empty-fhir-ig/.github/workflows/main.yml@master",
        # link: https://github.com/openhie/empty-fhir-ig/blob/master/.github/workflows/main.yml#L87
        # uses direct flow composite action tj-actions/branch-names@v4.3
    }],
    ObjectId('63dd9621045fe2c0b716405a'): [{
        "type" : "e",
        "reusable_workflow" : "blockscout/blockscout-ci-cd/.github/workflows/e2e_new.yaml@master",
        # link: https://github.com/blockscout/blockscout-ci-cd/blob/master/.github/workflows/e2e_new.yaml
        # uses direct flow composite action rlespinasse/github-slug-action@v4
    }],
    ObjectId('63dd95fa3c0647426a8cbe6d'):[{
        "type" : "b",
        "action" : "smartlyio/github-actions@release-action-node-v1",
        "action_type" : "composite_action",
        # link: https://github.com/smartlyio/github-actions/blob/release-action-node-v1/release-action-node/action.yml
        # uses direct flow composite action smartlyio/github-actions@check-branch-behind-v1
    }],
    ObjectId('63dd9624045fe2c0b7164075'):[{
        "type" : "e",
        "reusable_workflow" : "rstudio/shiny-workflows/.github/workflows/routine.yaml@v1",
        # link: https://github.com/rstudio/shiny-workflows/blob/v1/.github/workflows/routine.yaml#L176
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd9613045fe2c0b7163fe7'):[{
        "type" : "b",
        "action" : "CleverShuttle/gh-composite-actions/actions/merge-to-nonprod@v1",
        "action_type" : "composite_action",
        # link: none
        # uses direct flow composite action tj-actions/branch-names@v6 and has a taint souce github.head_ref
    }],
    ObjectId('63dd963180aa29a6fd488926'):[{
        "type" : "e",
        "reusable_workflow" : "rstudio/shiny-workflows/.github/workflows/routine.yaml@v1",
        # link: https://github.com/rstudio/shiny-workflows/blob/v1/.github/workflows/routine.yaml#L176
        # uses indirect flow (local) composite action rstudio/shiny-workflows/.github/internal/verify-no-new-commits@v1
    }],
    ObjectId('63dd95c880aa29a6fd4884a3'):[{
        "type" : "b",
        "action" : "smartlyio/github-actions@release-action-node-v1",
        "action_type" : "composite_action",
        # link: https://github.com/smartlyio/github-actions/blob/release-action-node-v1/release-action-node/action.yml
        # uses direct flow composite action smartlyio/github-actions@check-branch-behind-v1
    }],
    ObjectId('63dd95d080aa29a6fd4884f7'):[{
        "type" : "b",
        "action" : "smartlyio/github-actions@release-action-node-v1",
        "action_type" : "composite_action",
        # link: https://github.com/smartlyio/github-actions/blob/release-action-node-v1/release-action-node/action.yml
        # uses direct flow composite action smartlyio/github-actions@check-branch-behind-v1
    }],
    ObjectId('63dd95eb80aa29a6fd488638'):[{
        "type" : "b",
        "action" : "APN-Pucky/fast-forward-action@main",
        "action_type" : "composite_action",
        # link: https://github.com/APN-Pucky/fast-forward-action/blob/main/action.yml#L20
        # uses direct flow composite action APN-Pucky/fast-forward-action/label@main
    }],
    ObjectId('63dd961e3c0647426a8cbfcd'):[{
        "type" : "e",
        "reusable_workflow" : "pharmaverse/admiralci/.github/workflows/check-templates.yml@main",
        # link: https://github.com/pharmaverse/admiralci/blob/main/.github/workflows/check-templates.yml#L41
        # uses direct flow composite action tj-actions/branch-names@v5.4
    }],
    ObjectId('63dd95c93c0647426a8cbc22'):[{
        "type" : "b",
        "action" : "team-gsri/actions-arma-tools/release-mission@v0",
        "action_type" : "composite_action",
        # link: https://github.com/team-gsri/actions-arma-tools/blob/v0/release-mission/action.yml
        # uses direct flow composite action arwynfr/actions-conventional-versioning/get-newVersion@v1 and arwynfr/actions-conventional-versioning@v1
    }]
}

hardcoded_wrong_type_14 = {
    ObjectId('63dd949080aa29a6fd4869f4'):[{
        "type" : "e",
        "reusable_workflow" : "VirtoCommerce/.github/.github/workflows/publish-docker.yml@v3.200.14",
        # link: https://github.com/VirtoCommerce/.github/blob/v3.200.14/.github/workflows/publish-docker.yml
        # uses direct flow javascript action VirtoCommerce/vc-github-actions/docker-load-image@master and VirtoCommerce/vc-github-actions/publish-docker-image@master
    },{
        "type" : "e",
        "reusable_workflow" : "VirtoCommerce/.github/.github/workflows/deploy.yml@v3.200.14",
        # link: https://github.com/VirtoCommerce/.github/blob/v3.200.14/.github/workflows/deploy.yml
        # uses direct flow javascript action VirtoCommerce/vc-github-actions/get-deploy-param@master and VirtoCommerce/vc-github-actions/create-deploy-pr@master
    },{
        "type" : "e",
        "reusable_workflow" : "VirtoCommerce/.github/.github/workflows/deploy-cloud.yml@v3.200.14",
        # link: https://github.com/VirtoCommerce/.github/blob/v3.200.14/.github/workflows/deploy-cloud.yml
        # uses direct flow javascript action VirtoCommerce/vc-github-actions/get-deploy-param@master and VirtoCommerce/vc-github-actions/cloud-create-deployment@master
    }],
    ObjectId('63dd949180aa29a6fd486a06'): [{
        "type" : "e",
        "reusable_workflow" : "VirtoCommerce/.github/.github/workflows/publish-docker.yml@v3.200.7",
        # link: https://github.com/VirtoCommerce/.github/blob/v3.200.7/.github/workflows/publish-docker.yml
        # uses direct flow javascript action VirtoCommerce/vc-github-actions/docker-load-image@master and VirtoCommerce/vc-github-actions/publish-docker-image@master
    },{
        "type" : "e",
        "reusable_workflow" : "VirtoCommerce/.github/.github/workflows/deploy.yml@v3.200.7",
        # link: https://github.com/VirtoCommerce/.github/blob/v3.200.7/.github/workflows/deploy.yml
        # uses direct flow javascript action VirtoCommerce/vc-github-actions/get-deploy-param@master and VirtoCommerce/vc-github-actions/create-deploy-pr@master
    }
    ]
}