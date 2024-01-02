<template>
  <div>

    <div class="alert alert-warning alert-dismissible fade show" role="alert">
      <strong>Here</strong> datatables will rise.
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>

    <div id="edit_form" v-if="editing" class="edit-section col-md-6 ">
        <h2><div v-if="adding">Add user</div><div v-else>Edit user "form.username"</div></h2>
        <form @submit.prevent="onSubmitForm">
          <slot name="editForm"></slot>

          <button
              class="btn btn-primary me-1"
              type="submit"
          >Submit</button>

          <button
              @click.prevent="editing = adding = false"
              class="btn btn-secondary"
              type="button"
          >Cancel</button>
        </form>
    </div>


    <div v-if="!editing" class="table-section">
        <h2>[[ capitalize(title) ]]</h2>
            <div v-if="totalRows>0" class="form-row">

                <div class="col-sm-7 my-2">
                    <button
                            @click="editing = adding = true"
                            class="btn btn-primary">
                            <i class="fa fa-plus"></i>
                            <span class="d-none d-md-inline"> Add [[capitalize(title_s)]]</span>
                    </button>
                    <!-- <small v-if="Object.keys(selected).length===0" class="text-muted ms-2"> -->
                    <small v-if="!selected.length" class="text-muted ms-2">
                      Click a row to edit or delete.
                    </small>
                    <span v-else>
                        <button
                                @click="editing = true"
                                class="btn btn-secondary ms-1">
                                <i class="fa fa-pencil"></i>
                                <span class="d-none d-md-inline"> Edit</span>
                        </button>
                        <button
                                @click="showMsgBoxConfirm"
                                class="btn btn-secondary ms-1">
                                <i class="fa fa-trash">
                                </i><span class="d-none d-md-inline"> Delete</span>
                        </button>
                    </span>
                </div>

                <div class="col-sm-5 my-2">
                    <!-- filter box -->
                </div>
            </div>

        <!-- <table-bare :items="items"
                   :fields="fields"
                   :sort-by="sortBy"
                   :sort-desc="sortDesc"
                   @changeSortBy="changeSortBy"
                   @rowClick="rowClick"
        ></table-bare> -->
        <!-- table section -->
        <!-- <template> -->
          <table class="table table-hover">
              <thead>
                  <tr>
                      <th v-for="(fld, index) in fields" v-bind:key="index"
                          @click="onHeaderClick(fld)"
                      >
                          <span v-if="(typeof fld==='string')" >
                              [[fld]]
                          </span>
                          <span v-else>[[fld.key]]
                              <i v-if="(['true', true].includes(fld.sortable))" 
                                  class="fas"
                                  :class="{'fa-sort sort-off': sortBy!=fld.key,
                                    'fa-sort-down': sortBy==fld.key && !sortDesc,
                                    'fa-sort-up': sortBy==fld.key && sortDesc,
                                    }"
                                  >
                              </i>
                          </span>
                          <span 
                              v-if="typeof fld==='string' ? sortBy==fld : sortBy==fld.key " 
                              class="badge text-bg-light sort-badge"
                              @click.stop="onClickSortBadge">x</span>
                      </th>
                  </tr>
              </thead>
              <tbody>
                  <tr v-for="(v1, k1) in items" v-bind:key="k1"
                      :class="{'table-active' : v1.selected}"
                      @click="onRowClick(v1, k1)">
                      <td v-for="(v2, k2) in v1" v-bind:key="k2">
                          <template v-if="fields_simple.includes(k2)">[[v2]]</template></td>
                  </tr>
              </tbody>
          </table>
      <!-- </template> -->


        <div v-if="totalRows>0" class="row">
            <div class="col-md-2 mb-1">
                <select v-model="perPage" class="form-select" id="perPageOptions">
                  <option v-for="(opt, idx) in perPageOptions" v-bind:key="idx" :value="opt.value" >
                    [[opt.label]]
                  </option>
                </select>
            </div>
            <div class="col-md-8 mb-1">
              <pagination-bare
                :current-page="currentPage"
                :total-rows="totalRows"
                :per-page="perPage"
                @pageChanged="pageChanged"
              ></pagination-bare>
            </div>
        </div>

    </div>
    <!-- <div v-else>No data to display.</div> -->
    <input v-model
  </div>
</template>



<script>
import useDataTable from '@/components/dataTable.js';
import { useCapitalize } from '@/composables/stringUtils';
import useTable from '@/components/table.js';
// import { ref } from 'vue';
import TableBare from '@/components/tableBare.vue';
import PaginationBare from '@/components/paginationBare.vue';

export default {
    name: 'data-table',
    components: {
    PaginationBare,
    
},
    props: ['apiEndpoint'],
    setup(props, ctx) {

        const { flashMessage, flashMessageVariant, 
          adding, editing, title, selected, items, fields,
          currentPage, perPage, perPageOptions, totalRows,
          onRowSelected, onFiltered,
          onSortChanged, onSubmitForm, onPageChange,
          unselectRows,
          sortBy, sortDesc, filter } = useDataTable();

        const { fields_simple } = useTable(ctx, fields, sortBy, sortDesc);
        console.log(props.apiEndpoint)

        // mutate title
        var title_s
        let title_temp
        title_temp = title.value.split('|')
        title_s = title_temp[0]
        title.value = title_temp.length > 1 ? title_temp[1] : title_temp[0]

        editing.value = false
        
        function showMsgBoxConfirm() {
          // dummy
        }

        function pageChanged(page) {
          currentPage.value = page
          // fetchData('page')
        }

        function onRowClick(rowData, idx) {
          unselectRows(idx)
          rowData.selected = !rowData.selected
          selected.value = rowData.selected ? [rowData] : []
          console.log(selected.value)
        }

        function changeSortBy(sortByVal, sortDescVal) {
          sortBy.value = sortByVal
          sortDesc.value = sortDescVal
        }

        return { 
            flashMessage,
            flashMessageVariant,
            adding,
            editing,
            title, title_s,
            showMsgBoxConfirm,
            selected,
            capitalize:useCapitalize,
            items, fields,
            currentPage, perPage, perPageOptions, totalRows,
            sortBy, sortDesc, filter,
            onRowSelected, onFiltered, onSortChanged,
            onSubmitForm, onPageChange,
            changeSortBy, 
            pageChanged,

            fields_simple, onRowClick,
            }
    }
}

export {PaginationBare, TableBare };
</script>

<style scoped>
  @import 'bootstrap/dist/css/bootstrap.min.css';

  .sort-off {
      color: lightgray
  }

  .sort-badge {
      cursor: pointer;
      float: right;
  }

</style>