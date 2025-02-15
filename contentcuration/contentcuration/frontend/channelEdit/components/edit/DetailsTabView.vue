<template>

  <div v-if="nodes.length" class="details-edit-view">
    <VForm ref="form" v-model="valid" :lazy-validation="newContent" class="px-2">
      <!-- File upload and preview section -->
      <template v-if="oneSelected && allResources && !allExercises">
        <FileUpload
          v-if="oneSelected && allResources && !allExercises"
          :key="firstNode.id"
          :nodeId="firstNode.id"
          @previewClick="trackPreview"
        />
      </template>

      <!-- Basic information section -->
      <VLayout row wrap class="section">
        <VFlex xs12>
          <h1 class="subheading">
            {{ $tr('basicInfoHeader') }}
          </h1>
          <!-- Title -->
          <VTextField
            v-if="oneSelected"
            ref="title"
            v-model="title"
            maxlength="200"
            counter
            :rules="titleRules"
            :label="$tr('titleLabel')"
            autofocus
            required
            box
            @focus="trackClick('Title')"
          />
          <VLayout row wrap>
            <VFlex
              xs12
              md6
              class="basicInfoColumn"
              :class="{ 'pr-2': $vuetify.breakpoint.mdAndUp }"
            >
              <!-- Description -->
              <VTextarea
                v-if="oneSelected"
                ref="description"
                v-model="description"
                :label="$tr('descriptionLabel')"
                maxlength="400"
                counter
                autoGrow
                box
                height="100%"
                class="descriptionTextArea"
                @focus="trackClick('Description')"
              />
            </VFlex>
            <VFlex xs12 md6 :class="{ 'pl-2': $vuetify.breakpoint.mdAndUp }">
              <!-- Learning activity -->
              <LearningActivityOptions
                id="learning_activities"
                ref="learning_activities"
                v-model="contentLearningActivities"
                :disabled="isTopic"
                @focus="trackClick('Learning activities')"
              />
              <!-- Level -->
              <LevelsOptions
                id="levels"
                ref="contentLevel"
                v-model="contentLevel"
                @focus="trackClick('Levels dropdown')"
              />
              <!-- What you will need -->
              <ResourcesNeededOptions
                id="resources_needed"
                ref="resourcesNeeded"
                v-model="resourcesNeeded"
                @focus="trackClick('What you will need')"
              />
              <!-- Tags -->
              <VCombobox
                ref="tags"
                v-model="contentTags"
                class="tagbox"
                :items="tags"
                :searchInput.sync="tagText"
                chips
                box
                :label="$tr('tagsLabel')"
                multiple
                deletableChips
                hideSelected
                maxlength="30"
                autoSelectFirst
                @focus="trackClick('Tags')"
              >
                <template #no-data>
                  <VListTile v-if="tagText && tagText.trim()">
                    <VListTileContent>
                      <VListTileTitle>
                        {{ $tr('noTagsFoundText', { text: tagText.trim() }) }}
                      </VListTileTitle>
                    </VListTileContent>
                  </VListTile>
                </template>
              </VCombobox>
            </VFlex>
          </VLayout>
          <!-- Category -->
          <CategoryOptions ref="categories" v-model="categories" />
        </VFlex>
      </VLayout>

      <!-- Completion section for exercises -->
      <VLayout v-if="allExercises" row wrap class="section">
        <VFlex xs12>
          <h1 class="subheading">
            {{ $tr('assessmentOptionsLabel') }}
          </h1>
          <!-- Randomize question order -->
          <Checkbox
            ref="randomize"
            v-model="randomizeOrder"
            :label="$tr('randomizeQuestionLabel')"
            :indeterminate="!isUnique(randomizeOrder)"
          />
        </VFlex>
      </VLayout>

      <!-- Completion section for all resources -->
      <VLayout v-if="!isTopic" row wrap class="section">
        <VFlex xs12>
          <h1 class="subheading">
            {{ $tr('completionLabel') }}
          </h1>
          <!-- Checkbox for "Allow learners to mark complete" -->
          <VFlex md6 class="pb-2">
            <Checkbox
              v-model="learnerManaged"
              color="primary"
              :label="$tr('learnersCanMarkComplete')"
              style="margin-top: 0px; padding-top: 0px"
            />
          </VFlex>
          <CompletionOptions
            v-model="completionAndDuration"
            :kind="firstNode.kind"
            :fileDuration="fileDuration"
            :required="!isDocument"
            :practiceQuizzesAllowed="allowChannelQuizzes"
          />
        </VFlex>
      </VLayout>

      <!-- Thumbnail section -->
      <VLayout row wrap class="section">
        <VFlex v-if="oneSelected" xs12>
          <h1 class="subheading">
            {{ $tr('thumbnailHeader') }}
          </h1>
          <!-- Thumbnail -->
          <div style="width: 250px">
            <ContentNodeThumbnail
              v-model="thumbnail"
              :nodeId="firstNode.id"
              :encoding="thumbnailEncoding"
              @encoded="setEncoding"
            />
          </div>
        </VFlex>
      </VLayout>

      <!-- Audience section -->
      <VLayout row wrap class="section">
        <VFlex xs12>
          <h1 class="subheading">
            {{ $tr('audienceHeader') }}
          </h1>
          <!-- Language -->
          <LanguageDropdown
            id="language"
            ref="language"
            v-model="language"
            class="mb-2"
            :hint="languageHint"
            :placeholder="getPlaceholder('language')"
            clearable
            persistent-hint
            @focus="trackClick('Language')"
          />

          <!-- Visibility -->
          <VisibilityDropdown
            v-if="allResources"
            id="role_visibility"
            ref="role_visibility"
            v-model="role"
            :placeholder="getPlaceholder('role')"
            :required="isUnique(role)"
            @focus="trackClick('Role visibility')"
          />
        </VFlex>
      </VLayout>

      <!-- Accessibility section -->
      <VLayout row wrap class="section">
        <template v-if="requiresAccessibility">
          <VFlex xs12>
            <h1 class="subheading">
              {{ translateMetadataString('accessibility') }}
            </h1>
            <AccessibilityOptions
              v-model="accessibility"
              :checked="accessibility"
              :kind="firstNode.kind"
            />
          </VFlex>
        </template>
      </VLayout>

      <!-- Source section -->
      <VLayout row wrap class="section">
        <template v-if="allResources">
          <VFlex xs12 class="auth-section">
            <h1 class="subheading">
              {{ $tr('sourceHeader') }}
            </h1>
            <p v-if="disableAuthEdits" class="grey--text">
              {{ detectedImportText }}
            </p>
            <p v-if="oneSelected && isImported">
              <ActionLink
                :href="importedChannelLink"
                target="_blank"
                :text="$tr('importedFromButtonText', { channel: importedChannelName })"
              />
            </p>

            <!-- Author -->
            <VCombobox
              ref="author"
              :items="authors"
              :label="$tr('authorLabel')"
              :readonly="disableAuthEdits"
              maxlength="200"
              counter
              autoSelectFirst
              box
              :placeholder="getPlaceholder('author')"
              :value="author && author.toString()"
              @input.native="(e) => (author = e.srcElement.value)"
              @input="author = $event"
              @focus="trackClick('Author')"
            >
              <template #append-outer>
                <HelpTooltip :text="$tr('authorToolTip')" top :small="false" />
              </template>
            </VCombobox>

            <!-- Provider -->
            <VCombobox
              ref="provider"
              :items="providers"
              :label="$tr('providerLabel')"
              :readonly="disableAuthEdits"
              maxlength="200"
              counter
              :placeholder="getPlaceholder('provider')"
              autoSelectFirst
              box
              :value="provider && provider.toString()"
              @input.native="(e) => (provider = e.srcElement.value)"
              @input="provider = $event"
              @focus="trackClick('Provider')"
            >
              <template #append-outer>
                <HelpTooltip :text="$tr('providerToolTip')" top :small="false" />
              </template>
            </VCombobox>

            <!-- Aggregator -->
            <VCombobox
              ref="aggregator"
              :items="aggregators"
              :label="$tr('aggregatorLabel')"
              :readonly="disableAuthEdits"
              maxlength="200"
              counter
              autoSelectFirst
              :placeholder="getPlaceholder('aggregator')"
              box
              :value="aggregator && aggregator.toString()"
              @input.native="(e) => (aggregator = e.srcElement.value)"
              @input="aggregator = $event"
              @focus="trackClick('Aggregator')"
            >
              <template #append-outer>
                <HelpTooltip :text="$tr('aggregatorToolTip')" top :small="false" />
              </template>
            </VCombobox>

            <!-- License -->
            <LicenseDropdown
              id="license"
              ref="license"
              v-model="licenseItem"
              :required="isUnique(license) && isUnique(license_description) && !disableAuthEdits"
              :readonly="disableAuthEdits"
              :placeholder="getPlaceholder('license')"
              :descriptionPlaceholder="getPlaceholder('license_description')"
              @focus="trackClick('License')"
              @descriptionFocus="trackClick('License description')"
            />

            <!-- Copyright Holder -->
            <VCombobox
              v-if="copyrightHolderRequired"
              ref="copyright_holder"
              :items="copyrightHolders"
              :label="$tr('copyrightHolderLabel')"
              maxlength="200"
              counter
              :required="isUnique(copyright_holder) && !disableAuthEdits"
              :rules="copyrightHolderRules"
              :placeholder="getPlaceholder('copyright_holder')"
              autoSelectFirst
              :readonly="disableAuthEdits"
              box
              :value="copyright_holder && copyright_holder.toString()"
              @input.native="(e) => (copyright_holder = e.srcElement.value)"
              @input="copyright_holder = $event"
              @focus="trackClick('Copyright holder')"
            />
          </VFlex>
        </template>
      </VLayout>

      <!-- Subtitles -->
      <VLayout v-if="videoSelected" row wrap class="section">
        <VFlex xs12>
          <SubtitlesList
            :nodeId="firstNode.id"
            @addFile="subtitleFileLanguageComparison"
          />
        </VFlex>
      </VLayout>

      <!-- Audio accessibility section -->
      <VLayout row wrap class="section">
        <template v-if="audioAccessibility">
          <VFlex xs12>
            <SubtitlesList :nodeId="firstNode.id" />
          </VFlex>
        </template>
      </VLayout>
    </VForm>
  </div>

</template>

<script>

  import difference from 'lodash/difference';
  import intersection from 'lodash/intersection';
  import uniq from 'lodash/uniq';
  import { mapGetters, mapActions } from 'vuex';
  import ContentNodeThumbnail from '../../views/files/thumbnails/ContentNodeThumbnail';
  import FileUpload from '../../views/files/FileUpload';
  import SubtitlesList from '../../views/files/supplementaryLists/SubtitlesList';
  import { isImportedContent, importedChannelLink } from '../../utils';
  import AccessibilityOptions from './AccessibilityOptions.vue';
  import LevelsOptions from './LevelsOptions.vue';
  import ResourcesNeededOptions from './ResourcesNeededOptions.vue';
  import LearningActivityOptions from './LearningActivityOptions.vue';
  import CategoryOptions from './CategoryOptions.vue';
  import CompletionOptions from './CompletionOptions.vue';
  import FormatPresetsMap, { FormatPresetsNames } from 'shared/leUtils/FormatPresets';
  import {
    getTitleValidators,
    getCopyrightHolderValidators,
    translateValidator,
  } from 'shared/utils/validation';
  import { findLicense, memoizeDebounce } from 'shared/utils/helpers';
  import LanguageDropdown from 'shared/views/LanguageDropdown';
  import HelpTooltip from 'shared/views/HelpTooltip';
  import LicenseDropdown from 'shared/views/LicenseDropdown';
  import VisibilityDropdown from 'shared/views/VisibilityDropdown';
  import Checkbox from 'shared/views/form/Checkbox';
  import { ContentKindsNames } from 'shared/leUtils/ContentKinds';
  import { NEW_OBJECT, FeatureFlagKeys, AccessibilityCategories } from 'shared/constants';
  import { constantsTranslationMixin, metadataTranslationMixin } from 'shared/mixins';

  // Define an object to act as the place holder for non unique values.
  const nonUniqueValue = {};
  nonUniqueValue.toString = () => '';

  function getValueFromResults(results) {
    if (results.length === 0) {
      return null;
    } else if (results.length === 1) {
      return results[0];
    } else {
      return nonUniqueValue;
    }
  }

  function generateGetterSetter(key) {
    return {
      get() {
        return this.getValueFromNodes(key);
      },
      set(value) {
        this.update({ [key]: value });
      },
    };
  }

  function generateExtraFieldsGetterSetter(key, defaultValue) {
    return {
      get() {
        return this.getExtraFieldsValueFromNodes(key, defaultValue);
      },
      set(value) {
        this.updateExtraFields({ [key]: value });
      },
    };
  }

  /**
   * This function is used to generate getter/setters for new metadata fields that are boolean maps:
   * - `grade_levels` (sometimes referred to as `content_levels`)
   * - `learner_needs` (resources needed)
   * - `accessibility_labels` (accessibility options)
   * - `learning_activities` (learning activities)
   * - `categories` (categories)
   */

  function generateNestedNodesGetterSetter(key) {
    return {
      get() {
        const value = this.getValueFromNodes(key);
        return Object.keys(value);
      },
      set(value) {
        const newMap = {};
        for (let label of value) {
          newMap[label] = true;
        }
        this.update({ [key]: newMap });
      },
    };
  }

  export default {
    name: 'DetailsTabView',
    components: {
      LanguageDropdown,
      HelpTooltip,
      LicenseDropdown,
      VisibilityDropdown,
      FileUpload,
      SubtitlesList,
      ContentNodeThumbnail,
      Checkbox,
      AccessibilityOptions,
      LevelsOptions,
      ResourcesNeededOptions,
      LearningActivityOptions,
      CategoryOptions,
      CompletionOptions,
    },
    mixins: [constantsTranslationMixin, metadataTranslationMixin],
    props: {
      nodeIds: {
        type: Array,
        default: () => [],
      },
    },
    data() {
      return {
        tagText: null,
        valid: true,
        diffTracker: {},
      };
    },
    computed: {
      ...mapGetters('contentNode', [
        'getContentNodes',
        'authors',
        'providers',
        'aggregators',
        'copyrightHolders',
        'tags',
      ]),
      ...mapGetters('currentChannel', ['currentChannel']),
      ...mapGetters('file', ['getContentNodeFiles']),
      nodes() {
        return this.getContentNodes(this.nodeIds);
      },
      firstNode() {
        return this.nodes.length ? this.nodes[0] : null;
      },
      allExercises() {
        return this.nodes.every(node => node.kind === ContentKindsNames.EXERCISE);
      },
      allResources() {
        return !this.nodes.some(node => node.kind === ContentKindsNames.TOPIC);
      },
      isImported() {
        return isImportedContent(this.firstNode);
      },
      importedChannelLink() {
        return importedChannelLink(this.firstNode, this.$router);
      },
      importedChannelName() {
        return this.firstNode.original_channel_name;
      },
      requiresAccessibility() {
        return this.nodes.every(
          node => node.kind !== ContentKindsNames.AUDIO && node.kind !== ContentKindsNames.TOPIC
        );
      },
      audioAccessibility() {
        return this.oneSelected && this.firstNode.kind === 'audio';
      },
      /* FORM FIELDS */
      title: generateGetterSetter('title'),
      description: generateGetterSetter('description'),
      randomizeOrder: generateExtraFieldsGetterSetter('randomize', true),
      author: generateGetterSetter('author'),
      provider: generateGetterSetter('provider'),
      aggregator: generateGetterSetter('aggregator'),
      copyright_holder: generateGetterSetter('copyright_holder'),
      contentTags: {
        get() {
          return intersection(...this.nodes.map(node => node.tags));
        },
        set(value) {
          const oldValue = intersection(...this.nodes.map(node => node.tags));
          // If selecting a tag, clear the text field
          if (value.length > (oldValue || []).length) {
            this.tagText = null;
            this.addNodeTags(difference(value, oldValue));
          } else {
            this.removeNodeTags(difference(oldValue, value));
          }
        },
      },
      role: generateGetterSetter('role_visibility'),
      language: generateGetterSetter('language'),
      accessibility: generateNestedNodesGetterSetter('accessibility_labels'),
      contentLevel: generateNestedNodesGetterSetter('grade_levels'),
      resourcesNeeded: generateNestedNodesGetterSetter('learner_needs'),
      contentLearningActivities: generateNestedNodesGetterSetter('learning_activities'),
      categories: generateNestedNodesGetterSetter('categories'),
      license() {
        return this.getValueFromNodes('license');
      },
      license_description() {
        return this.getValueFromNodes('license_description');
      },
      licenseItem: {
        get() {
          return {
            license: this.license && this.license.toString() ? this.license : null,
            license_description: (this.license_description || '').toString(),
          };
        },
        set(value) {
          this.update(value);
        },
      },
      thumbnail: {
        get() {
          return this.nodeFiles.find(f => f.preset.thumbnail);
        },
        set(file) {
          file ? this.updateFile(file) : this.thumbnail ? this.deleteFile(this.thumbnail) : null;
        },
      },
      thumbnailEncoding: generateGetterSetter('thumbnail_encoding'),
      completionAndDuration: {
        get() {
          const { completion_criteria, modality } =
            this.getExtraFieldsValueFromNodes('options') || {};
          const suggested_duration_type = this.getExtraFieldsValueFromNodes(
            'suggested_duration_type'
          );
          const suggested_duration = this.getValueFromNodes('suggested_duration');
          return {
            suggested_duration,
            suggested_duration_type,
            modality,
            ...(completion_criteria || {}),
          };
        },
        set({ completion_criteria, suggested_duration, suggested_duration_type, modality }) {
          completion_criteria.learner_managed = this.learnerManaged;
          const options = { completion_criteria, modality };
          this.updateExtraFields({ options });
          this.updateExtraFields({ suggested_duration_type });
          this.update({ suggested_duration });
        },
      },
      learnerManaged: {
        get() {
          const { completion_criteria = {} } = this.getExtraFieldsValueFromNodes('options') || {};
          return completion_criteria.learner_managed;
        },
        set(value) {
          const { completion_criteria = {}, ...options } =
            this.getExtraFieldsValueFromNodes('options') || {};
          completion_criteria.learner_managed = value;
          this.updateExtraFields({ options: { ...options, completion_criteria } });
        },
      },
      /* COMPUTED PROPS */
      disableAuthEdits() {
        return this.nodes.some(node => node.freeze_authoring_data);
      },
      detectedImportText() {
        const count = this.nodes.filter(node => node.freeze_authoring_data).length;
        return this.$tr('detectedImportText', { count });
      },
      oneSelected() {
        return this.nodes.length === 1;
      },
      languageHint() {
        let topLevel = this.nodes.some(node => node.parent === this.currentChannel.main_tree);
        return topLevel ? this.$tr('languageChannelHelpText') : this.$tr('languageHelpText');
      },
      copyrightHolderRequired() {
        // Needs to appear when any of the selected licenses require a copyright holder
        return this.nodes.some(
          node =>
            findLicense(node.license, { copyright_holder_required: false })
              .copyright_holder_required
        );
      },
      titleRules() {
        return getTitleValidators().map(translateValidator);
      },
      copyrightHolderRules() {
        if (this.disableAuthEdits || !this.isUnique(this.copyright_holder)) {
          return [];
        }
        return getCopyrightHolderValidators().map(translateValidator);
      },
      nodeFiles() {
        return (this.firstNode && this.getContentNodeFiles(this.firstNode.id)) || [];
      },
      fileDuration() {
        if (
          this.firstNode.kind === ContentKindsNames.AUDIO ||
          this.firstNode.kind === ContentKindsNames.VIDEO
        ) {
          // filter for the correct file types,
          // to exclude files such as subtitle or cc
          let audioVideoFiles;
          audioVideoFiles = this.nodeFiles.filter(file => this.allowedFileType(file));
          // return the last item in the array
          const file = audioVideoFiles[audioVideoFiles.length - 1];
          return file.duration;
        } else {
          return null;
        }
      },
      videoSelected() {
        return this.oneSelected && this.firstNode.kind === ContentKindsNames.VIDEO;
      },
      newContent() {
        return !this.nodes.some(n => n[NEW_OBJECT]);
      },
      allowChannelQuizzes() {
        return this.$store.getters.hasFeatureEnabled(FeatureFlagKeys.channel_quizzes);
      },
      isDocument() {
        return this.firstNode.kind === ContentKindsNames.DOCUMENT;
      },
      isTopic() {
        return this.firstNode.kind === ContentKindsNames.TOPIC;
      },
    },
    watch: {
      nodes: {
        deep: true,
        handler() {
          // Handles both when loading a node and when making a change
          this.tagText = null;
          this.$nextTick(this.handleValidation);
        },
      },
    },
    mounted() {
      this.$nextTick(this.handleValidation);
    },
    methods: {
      ...mapActions(['setUnsavedChanges']),
      ...mapActions('contentNode', ['updateContentNode', 'addTags', 'removeTags']),
      ...mapActions('file', ['updateFile', 'deleteFile']),
      saveNode: memoizeDebounce(
        function(id) {
          this.saveFromDiffTracker(id);
        },
        1000,
        { trailing: true }
      ),
      saveFromDiffTracker(id) {
        if (this.diffTracker[id]) {
          return this.updateContentNode({ id, ...this.diffTracker[id] }).then(() => {
            delete this.diffTracker[id];
          });
        }
        return Promise.resolve();
      },
      /*
       * @public
       */
      immediateSaveAll() {
        return Promise.all(Object.keys(this.diffTracker).map(this.saveFromDiffTracker));
      },
      update(payload) {
        this.nodeIds.forEach(id => {
          this.$set(this.diffTracker, id, {
            ...(this.diffTracker[id] || {}),
            ...payload,
          });
          this.setUnsavedChanges(true);
          this.saveNode(id);
        });
      },
      updateExtraFields(extra_fields) {
        this.nodeIds.forEach(id => {
          const existingData = this.diffTracker[id] || {};
          this.$set(this.diffTracker, id, {
            ...existingData,
            extra_fields: {
              ...(existingData.extra_fields || {}),
              ...extra_fields,
            },
          });
          this.setUnsavedChanges(true);
          this.saveNode(id);
        });
      },
      addNodeTags(tags) {
        this.addTags({ ids: this.nodeIds, tags });
      },
      removeNodeTags(tags) {
        this.removeTags({ ids: this.nodeIds, tags });
      },
      isUnique(value) {
        return value !== nonUniqueValue;
      },
      allowedFileType(file) {
        let allowedFileTypes = [];
        // add the relevant format presets for audio and video
        // high res and low res are currently the same, so only one is included
        allowedFileTypes.push(
          FormatPresetsMap.get(FormatPresetsNames.HIGH_RES_VIDEO).allowed_formats
        );
        allowedFileTypes.push(FormatPresetsMap.get(FormatPresetsNames.AUDIO).allowed_formats);
        allowedFileTypes = allowedFileTypes.flat();
        return allowedFileTypes.includes(file.file_format);
      },
      getValueFromNodes(key) {
        const results = uniq(
          this.nodes.map(node => {
            if (Object.prototype.hasOwnProperty.call(this.diffTracker[node.id] || {}, key)) {
              return this.diffTracker[node.id][key];
            }
            return node[key] || null;
          })
        );
        return getValueFromResults(results);
      },
      getExtraFieldsValueFromNodes(key, defaultValue = null) {
        const results = uniq(
          this.nodes.map(node => {
            if (
              Object.prototype.hasOwnProperty.call(
                this.diffTracker[node.id] || {},
                'extra_fields'
              ) &&
              Object.prototype.hasOwnProperty.call(this.diffTracker[node.id].extra_fields, key)
            ) {
              return this.diffTracker[node.id].extra_fields[key];
            }
            return node.extra_fields[key] || defaultValue;
          })
        );
        return getValueFromResults(results);
      },
      getPlaceholder(field) {
        // Should only show if multiple nodes are selected with different
        // values for the field (e.g. if author field is different on the selected nodes)
        return this.oneSelected || this.isUnique(this[field]) ? '' : '---';
      },
      handleValidation() {
        if (this.$refs.form) {
          !this.newContent ? this.$refs.form.resetValidation() : this.$refs.form.validate();
        }
      },
      setEncoding(encoding) {
        this.thumbnailEncoding = encoding;
      },
      trackClick(label) {
        this.$analytics.trackClick('channel_editor_modal_details', label);
      },
      trackPreview() {
        this.$analytics.trackAction('channel_editor_modal_preview', 'Preview', {
          eventLabel: 'File',
        });
      },
      subtitleFileLanguageComparison(file) {
        if (this.oneSelected && this.language === file.language) {
          this.accessibility = [...this.accessibility, AccessibilityCategories.CAPTIONS_SUBTITLES];
        }
      },
    },
    $trs: {
      basicInfoHeader: 'Basic information',
      audienceHeader: 'Audience',
      sourceHeader: 'Source',
      thumbnailHeader: 'Thumbnail',
      titleLabel: 'Title',
      languageHelpText: 'Leave blank to use the folder language',
      languageChannelHelpText: 'Leave blank to use the channel language',
      importedFromButtonText: 'Imported from {channel}',
      detectedImportText:
        '{count, plural,\n =1 {# resource has view-only permission}\n other {# resources have view-only permission}}',
      authorLabel: 'Author',
      authorToolTip: 'Person or organization who created this content',
      providerLabel: 'Provider',
      providerToolTip: 'Organization that commissioned or is distributing the content',
      aggregatorLabel: 'Aggregator',
      aggregatorToolTip:
        'Website or org hosting the content collection but not necessarily the creator or copyright holder',
      copyrightHolderLabel: 'Copyright holder',
      descriptionLabel: 'Description',
      tagsLabel: 'Tags',
      noTagsFoundText: 'No results found for "{text}". Press \'Enter\' key to create a new tag',
      assessmentOptionsLabel: 'Assessment options',
      randomizeQuestionLabel: 'Randomize question order for learners',
      completionLabel: 'Completion',
      learnersCanMarkComplete: 'Allow learners to mark as complete',
    },
  };

</script>

<style lang="less" scoped>

  @space-between-sections: 64px;

  /deep/ a,
  /deep/ a:hover {
    color: inherit;
    text-decoration: none;
  }

  .details-edit-view {
    padding: 10px;

    /deep/ .subheading {
      margin-bottom: 8px;
      font-weight: bold;
    }

    .section .flex {
      margin: 24px 0 !important;
    }

    .auth-section {
      /deep/ .v-autocomplete .v-input__append-inner {
        visibility: hidden;
      }
    }

    .v-form {
      max-width: 960px;

      .tagbox {
        /deep/ .v-select__selections {
          min-height: 0 !important;
        }

        /deep/ .v-chip__content {
          color: black; // Read-only tag box grays out tags
        }

        /deep/ .v-input__append-inner {
          display: none;
        }
      }

      /deep/ .v-input--is-readonly {
        /deep/ label {
          color: var(--v-grey-darken2) !important;
        }

        /deep/ .v-input__append-inner {
          display: none;
        }

        /deep/ .v-input__slot {
          &::before {
            border-style: dotted;
          }

          &::after {
            border: 0;
          }
        }
      }

      .basicInfoColumn {
        display: flex;

        /deep/ .v-input {
          // Stretches the "Description" text area to fill the column vertically
          align-items: stretch;
        }

        /deep/ .v-input__control {
          // Makes sure that the character count does not get pushed to second column
          flex-wrap: nowrap;
        }
      }
    }
  }

</style>
