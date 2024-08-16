//vueLinkTable.js

import { addStyles, formatColumnTitle } from './vueTableUtils.js';

const template = `
<div >
    <nav aria-label="breadcrumb">
        <ol class="breadcrumb">
            <li class="breadcrumb-item"><a href="#" @click="onClickBaseCrumb">{{title}}</a></li>
            <li class="breadcrumb-item active" aria-current="page">{{recordName}}</li>
        </ol>
    </nav>

    <div class="col-8 col-md-4 mb-2">
        <vue-add-item-panel
            :placeholder = placeholder
            :lookup-url = lookupUrl
            :link-fields = linkFields
            @itemSelected="onItemSelected"
        ></vue-add-item-panel>
    </div>

    <div v-if="isLoading" class="text-center my-3">
      <div>Loading...</div>
    </div>

    <table v-else class="table" :set="lkKey = linkKey">
        <thead>
            <tr >
                <th v-for="item in columnTitles(lkKey)">
                    {{formatColumnTitle(item)}}</th>
                <th>Action</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="(r, ind) in items[selectedIndex][lkKey]">
                <td v-for="fn in columnTitles(lkKey)">
                    {{r[fn] }}
                </td>
                <td><a href="#" @click.stop="onClickDelete(r['id'],ind)"><span class="fas fa-trash"></span></a></td>
            </tr>
        </tbody>
    </table>
    <div v-if="totalRows === 0">No data to show.</div>
    <div>
        <div  v-if="totalRows > 0" class="row">
            <div class="col-4 col-md-2">
                <select class="form-select" v-model="perPage">
                    <option v-for="i in perPageOptions" :value="i.value" >{{i.text}}</option>
                </select>
            </div>
            <div class="col-8 col-md-10">
                <vue-pagination
                 :current-page=currentPage :total-rows=totalRows :per-page=perPage
                 :key="paginationKey"
                 @pageChanged="onPageChanged"
                >
                </vue-pagination>
            </div>
        </div>
    </div>
</div>
`

const styles = `
    ul li:hover {
        background-color: #e9ecef;
    }
`
addStyles(styles)

const {ref, toRefs, watch, onMounted, computed } = Vue;

const initialPerPage = 10
const vueLinkTable = {
    props: ['title', 'links', 'linkKey', 'items', 'selectedIndex',
        'parentId', 'recordName'
    ],
    setup(props, ctx) {
        const storageKey = 'comp_link_perPage'
        const {title, links, linkKey, items, selectedIndex, parentId, 
            recordName} = toRefs(props)
        const flashMessage = ref('')
        const currentPage = ref(1)
        const perPage =  ref(initialPerPage)
        const perPageOptions = ref([
            {'value': 10, 'text': '10 items'},
            {'value': 25, 'text': '25 items'},
            {'value': 100, 'text': '100 items'},
        ])
        const lookupUrl = ref('')
        const isLoading = ref(false)
        const linkFields = ref('')

        const paginationKey = computed(() => `${perPage.value}-${totalRows.value}`)

        const placeholder = computed(() => getLinkByKey(linkKey.value).placeholder ||
            'Select an item to add...')

        const totalRows = computed(() => {
            return getLinkByKey(linkKey.value).totalRows[selectedIndex.value]
        }) 

        onMounted(() => {
            lookupUrl.value = `/links/${getLinkByKey(linkKey.value).link}`
            linkFields.value = getCurrentLink.fields.join(',')
            perPage.value = JSON.parse(localStorage.getItem(storageKey)) || 10
            fetch()
        })

        const getLinkByKey = (key) => links.value.find(el => el.key === key) || null
        const getCurrentLink = getLinkByKey(linkKey.value)

        const sendFMessage = (msg, mtype='info') => {
          if (msg === '' && flashMessage.value === '') return
          else {
            flashMessage.value = msg
            ctx.emit('messageChanged', flashMessage.value, mtype)
          }
        }

        watch(currentPage, (nv, ov) => { 
          fetch();  })
        
        watch(perPage, (nv, ov) => { 
            sendFMessage('')
            if (currentPage.value !== 1) {
              currentPage.value = 1
            } else {
              localStorage.setItem(storageKey, JSON.stringify(nv));
              fetch(); 
              }
            })

        const onItemSelected = async (itemId) => {
          addItem(itemId)
        }
         
        const onClickDelete = (itemId, itemIndex) => {
          deleteItem(parentId.value, itemId, itemIndex)
        }

        const onClickBaseCrumb = () => {
            sendFMessage('')
            ctx.emit('clickedHome')
        }
        
        const onPageChanged = (page) => {
          currentPage.value = page
        }

        const columnTitles = (key) => {
          const linkItem = getLinkByKey(key)
          return linkItem.fields ? linkItem.fields : ['No titles found!']
        }

        const fetch = async () => {
          const key = linkKey.value
          const linkItem = getLinkByKey(key)
          // const endPoint = linkItem.link + `/get/${parentId.value}`
          // const endPoint = linkItem.link + `/get?parent_id=${parentId.value}`
          const endPoint = `/links/${linkItem.link}/get?parent_id=${parentId.value}`
          const start = (currentPage.value - 1) * perPage.value
          const limit = perPage.value
          const linkFields = linkItem.fields.join(',')
          isLoading.value = true
          try {
            // const response = await axios.get(`${endPoint}?start=${start}&limit=${limit}&fields=${fields}`)
            const response = await axios.get(`${endPoint}&start=${start}&limit=${limit}&linkFields=${linkFields}`)
            const data = response.data
            items.value[selectedIndex.value][key] = data.data
          } catch (error) {
            console.log('Error in linkTable fetch:', error)
          } finally {
            isLoading.value = false
          }
        }

        const addItem = async (childId) => {
          try {
            const key = linkKey.value
            const linkItem = getLinkByKey(key)
            const linkFields = linkItem.fields
            // const endPoint = linkItem.link + `/new/${parentId.value}?id=${childId}&linkFields=${linkFields}`
            const endPoint = `/links/${linkItem.link}/new?parent_id=${parentId.value}&child_id=${childId}&linkFields=${linkFields}`
            const response = await axios.post(`${endPoint}`)
            const resp = response.data
            if (resp.result == 'ok') {
              items.value[selectedIndex.value][key].push(resp.data)
              linkItem.totalRows[selectedIndex.value] = Number(linkItem.totalRows[selectedIndex.value]) + 1
              sendFMessage(resp.message || 'New item added successfully.')
            } else {
              sendFMessage(resp.message, 'warning')
            }
          } catch (error) {
            console.log('Error in onItemSelected:', error)
          }
        }

        const deleteItem = async (parentId, childId, itemIndex) => {
          const linkItem = getLinkByKey(linkKey.value)
          // const endPoint = linkItem.link + `/delete/${parentId}?id=${childId}`
          const endPoint = `/links/${linkItem.link}/delete?parent_id=${parentId}&child_id=${childId}`
          try {
            const response = await axios.post(`${endPoint}`)
            const resp = response.data
            if (resp.result == 'ok') {
              items.value[selectedIndex.value][linkKey.value].splice(itemIndex, 1)
              linkItem.totalRows[selectedIndex.value] = Number(linkItem.totalRows[selectedIndex.value]) - 1
              sendFMessage(resp.message || 'Item successfuly deleted.')
            } else {
              sendFMessage(resp.message, 'warning')
            }
          } catch (error) {
            console.log('Error in linkTable delete:', error)
          }
        }

        return {
            onItemSelected, onClickDelete, onPageChanged, columnTitles,
            onClickBaseCrumb, formatColumnTitle,
            parentId, title, paginationKey, placeholder, lookupUrl, items,
            selectedIndex, recordName, linkKey, linkFields,
            currentPage, perPage, perPageOptions, totalRows, 
            flashMessage, isLoading,
        }
    },
    template: template,
    styles: styles,
}

export default vueLinkTable