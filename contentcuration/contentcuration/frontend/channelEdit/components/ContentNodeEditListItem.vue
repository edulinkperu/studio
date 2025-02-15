<template>

  <DraggableItem
    :draggableId="contentNode.id"
    :draggableMetadata="contentNode"
    :dragEffect="dragEffect"
    :dropEffect="draggableDropEffect"
    :beforeStyle="dragBeforeStyle"
    :afterStyle="dragAfterStyle"
  >
    <template #default>
      <ContentNodeListItem
        :node="contentNode"
        :compact="compact"
        :comfortable="comfortable"
        :active="active"
        :canEdit="canEdit"
        :draggableHandle="{
          grouped: selected,
          draggable,
          draggableMetadata: contentNode,
          effectAllowed: draggableEffectAllowed,
        }"
        :aria-selected="selected"
        class="content-node-edit-item"
        @infoClick="$emit('infoClick', $event)"
        @topicChevronClick="$emit('topicChevronClick', $event)"
      >
        <template #actions-start="{ hover }">
          <VListTileAction class="handle-col" :aria-hidden="!hover" @click.stop>
            <transition name="fade">
              <VBtn :disabled="copying" flat icon>
                <Icon color="#686868">
                  drag_indicator
                </Icon>
              </VBtn>
            </transition>
          </VListTileAction>
          <VListTileAction class="mx-2 select-col" @click.stop>
            <Checkbox
              v-model="selected"
              :disabled="copying"
              class="mt-0 pt-0"
              @dblclick.stop
            />
          </VListTileAction>
        </template>

        <template #actions-end>
          <VListTileAction :aria-hidden="!active" class="action-icon px-1">
            <Menu v-model="activated">
              <template #activator="{ on }">
                <IconButton
                  icon="optionsVertical"
                  :text="$tr('optionsTooltip')"
                  size="small"
                  :disabled="copying"
                  v-on="on"
                  @click.stop
                />
              </template>
              <ContentNodeOptions v-if="!copying" :nodeId="nodeId" />
            </Menu>
          </VListTileAction>
        </template>

        <template #context-menu="{ showContextMenu, positionX, positionY }">
          <ContentNodeContextMenu
            :show="showContextMenu"
            :positionX="positionX"
            :positionY="positionY"
            :nodeId="nodeId"
          />
        </template>
      </ContentNodeListItem>
    </template>
  </DraggableItem>

</template>


<script>

  import { mapGetters } from 'vuex';

  import ContentNodeContextMenu from './ContentNodeContextMenu';
  import ContentNodeOptions from './ContentNodeOptions';
  import ContentNodeListItem from './ContentNodeListItem';
  import Checkbox from 'shared/views/form/Checkbox';
  import IconButton from 'shared/views/IconButton';
  import DraggableItem from 'shared/views/draggable/DraggableItem';
  import { COPYING_FLAG } from 'shared/data/constants';
  import { DragEffect, DropEffect, EffectAllowed } from 'shared/mixins/draggable/constants';
  import { DraggableRegions } from 'frontend/channelEdit/constants';

  export default {
    name: 'ContentNodeEditListItem',
    components: {
      DraggableItem,
      ContentNodeListItem,
      ContentNodeOptions,
      ContentNodeContextMenu,
      Checkbox,
      IconButton,
    },
    props: {
      nodeId: {
        type: String,
        required: true,
      },
      select: {
        type: Boolean,
        default: false,
      },
      previewing: {
        type: Boolean,
        default: false,
      },
      compact: {
        type: Boolean,
        default: false,
      },
      comfortable: {
        type: Boolean,
        default: false,
      },
      /**
       * The `hasSelection` prop is used for disabling draggability specifically to handle
       * behaviors related to selecting and dragging multiple items.
       */
      /* eslint-disable-next-line kolibri/vue-no-unused-properties */
      hasSelection: {
        type: Boolean,
        default: false,
      },
    },
    data() {
      return {
        activated: false,
      };
    },
    computed: {
      ...mapGetters('currentChannel', ['canEdit']),
      ...mapGetters('contentNode', ['getContentNode']),
      ...mapGetters('draggable', ['activeDraggableRegionId']),
      selected: {
        get() {
          return this.select;
        },
        set(value) {
          this.$emit(value ? 'select' : 'deselect');
        },
      },
      active() {
        return this.selected || this.activated || this.previewing;
      },
      contentNode() {
        return this.getContentNode(this.nodeId);
      },
      draggable() {
        // TODO: When we allow selecting multiple and then dragging
        // return (this.selected || !this.hasSelection);
        return !this.copying;
      },
      copying() {
        return this.contentNode[COPYING_FLAG];
      },
      dragEffect() {
        return DragEffect.SORT;
      },
      draggableDropEffect() {
        if (!this.canEdit) {
          return DropEffect.NONE;
        }

        return this.activeDraggableRegionId === DraggableRegions.CLIPBOARD
          ? DropEffect.COPY
          : DropEffect.MOVE;
      },
      draggableEffectAllowed() {
        if (this.canEdit && !this.copying) {
          return EffectAllowed.COPY_OR_MOVE;
        } else if (!this.copying) {
          return EffectAllowed.COPY;
        }
        return EffectAllowed.NONE;
      },
      dragBeforeStyle() {
        return (size, height) => ({
          '::before': {
            height: `${height}px`,
          },
        });
      },
      dragAfterStyle() {
        return (size, height) => ({
          '::after': {
            height: `${height}px`,
          },
        });
      },
    },
    beforeDestroy() {
      // Unselect before removing
      if (this.selected) {
        this.selected = false;
      }
    },
    $trs: {
      optionsTooltip: 'Options',
    },
  };

</script>


<style lang="less" scoped>

  .content-node-edit-item {
    position: relative;
    transition: height ease 0.2s;

    &::before,
    &::after {
      display: block;
      width: 100%;
      height: 0;
      overflow: hidden;
      content: ' ';
      background: var(--v-draggableDropZone-base);
      transition: height ease 0.2s, bottom ease 0.2s;
    }

    &.active-draggable {
      overflow: hidden;

      &::before {
        position: absolute;
        top: 0;
        right: 0;
        bottom: 100%;
        left: 0;
        z-index: 1000;
        height: auto !important;
      }

      &::after {
        display: none;
      }

      &.dragging-over {
        &::before {
          bottom: 0;
        }
      }

      &:not(.dragging-over) {
        border-bottom: 0;
      }
    }
  }

  .select-col {
    width: 24px;
    min-width: 24px;
    opacity: 1;
  }

  .handle-col {
    width: 32px;
    min-width: 32px;
  }

  .handle-col .v-btn {
    margin-left: 2px !important;
    cursor: grab;
  }

  /deep/ .v-input--selection-controls__input {
    margin-right: 0;
  }

  .action-icon {
    display: flex;
    flex: 1 1 auto;
    align-items: flex-start;
    justify-content: center;
  }

</style>
