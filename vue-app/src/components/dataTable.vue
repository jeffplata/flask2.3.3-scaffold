<template>
  <div>

    <CAlert color="info" dismissible>
      <strong>Go right ahead</strong> and click that dimiss over there on the right.
    </CAlert>

    
    <div id="edit_form" v-if="editing" class="edit-section col-md-6 ">
        <h2><div v-if="adding">Add user</div><div v-else>Edit user "form.username"</div></h2>
        <form @submit.prevent="onSubmitForm">
          <slot name="editForm"></slot>

          <button
              type = "submit"
              variant="primary"
              class="mr-1"
          >Submit</button>

          <button
              @click="editing = adding = false"
              variant="secondary"
          >Cancel</button>
        </form>
    </div>


    <div v-if="!editing" class="table-section">
        <h2>[[ capitalize(title) ]]</h2>
            <div v-if="totalRows>0" class="form-row">

                <div class="col-sm-7 my-2">
                    <button
                            @click="editing = adding = true"
                            class="btn btn-primary"><i class="fa fa-plus"></i><span class="xxd-none d-md-inline"> Add [[capitalize(title_s)]]</span></button>
                    <span v-if="Object.keys(selected).length===0">
                    <small class="text-muted ml-2" >Click a row to edit or delete.</small>
                    </span>
                    <span v-else>
                        <button
                                @click="editing = true"
                                class="btn btn-secondary"><i class="fa fa-pencil"></i><span class="d-none d-md-inline"> Edit</span></button>
                        <button
                                @click="showMsgBoxConfirm"
                                class="btn btn-secondary"><i class="fa fa-trash"></i><span class="d-none d-md-inline"> Delete</span></button>
                    </span>
                </div>

                <div class="col-sm-5 my-2">
                    <!-- filter box -->
                </div>
            </div>

        <!-- table here -->
        <tableBare :items="items"
                   :fields="fields"
                   :sortBy="sortBy"
                   :sortDesc="sortDesc"
                   @changeSortBy="changeSortBy"
        ></tableBare>



        <div class="form-row">
          <b-input-group v-if="totalRows>0">
            <div class="col-xs-4 mr-2">
                <CFormSelect v-model="perPage" :options="perPageOptions" style="width:100px;"></CFormSelect>
            </div>
            <div class="col-xs-8">
              <b-pagination
                v-model="currentPage"
                :total-rows="totalRows"
                :per-page="perPage"
                aria-controls="my-table"
                @change="onPageChange"
              ></b-pagination>
            </div>
          </b-input-group>
        </div>

    </div>
    <!-- <div v-else>No data to display.</div> -->

  </div>
</template>



<script>
import DataTable from '@/components/dataTable.js';
import { useCapitalize } from '@/composables/stringUtils';
import { ref } from 'vue';
import tableBare from './tableBare.vue';
import { CAlert, CFormSelect,
        } from '@coreui/bootstrap-vue';


export default {
    components: {
      tableBare,
      CAlert, CFormSelect,
    },
    props: ['apiEndpoint'],
    setup(props) {

        const { flashMessage, flashMessageVariant, 
          adding, editing, title, selected, items, fields,
          currentPage, perPage, perPageOptions, totalRows,
          onRowSelected, onFiltered,
          onSortChanged, onSubmitForm, onPageChange,
          sortBy, sortDesc, filter } = DataTable();
        console.log(props.apiEndpoint)

        // mutate title
        var title_s
        let title_temp
        title_temp = title.value.split('|')
        title_s = title_temp[0]
        title.value = title_temp.length > 1 ? title_temp[1] : title_temp[0]

        editing.value = false
        
        const mybtableRef = ref(null)

        function showMsgBoxConfirm() {
          // dummy
        }

        function onRowClicked(item, index) {
          const mybtable = mybtableRef.value;
          console.log(mybtableRef.value)
          if (mybtable) {
            console.log('clicked')
            mybtable.selectRow(index)
          }
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
            onRowClicked, onRowSelected, onFiltered, onSortChanged,
            onSubmitForm, onPageChange,
            mybtableRef, changeSortBy,
            }
    }
}

</script>
