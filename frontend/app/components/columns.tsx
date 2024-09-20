"use client"

import { Button } from "@/components/ui/button"
import { ColumnDef } from "@tanstack/react-table"
import { MoreHorizontal } from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { ArrowUpDown } from "lucide-react"

import {
	CheckCircledIcon,
	CircleIcon,
	CrossCircledIcon,
	StopwatchIcon,
  } from "@radix-ui/react-icons"
import capitalizeFirstLetter from "../capitalize"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { useRef, useState } from "react"
import { useMediaQuery } from "react-responsive"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Drawer, DrawerContent, DrawerTrigger } from "@/components/ui/drawer"
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command"

// This type is used to define the shape of our data.
// You can use a Zod schema here if you want.
export type Payment = {
	id: string
	title: string
	status: "idle" | "in progress" | "done" | "canceled"
	category: string | null
	rating: string | null
	gm_url: string
	website: string | null
	phone: string | null
}

const status_to_icon = (status) => {
	switch (status){
		case 'idle':
			return CircleIcon
		case 'in progress':
			return StopwatchIcon
		case 'done':
			return CheckCircledIcon
		case 'canceled':
			return CrossCircledIcon
		default:
			return -1
	}
}

const status_icon = {
	"idle": CircleIcon,
	"in progress": StopwatchIcon,
	"done": CheckCircledIcon,
	"canceled": CrossCircledIcon
}

const categoryFilterFn = (row, columnId, filterValue) => {
	return filterValue.length === 0 || filterValue.includes(row.getValue(columnId));
};



export const columns: ColumnDef<Payment>[] = [
	{
		accessorKey: "title",
		header: ({column}) => {
			return <Button variant="ghost" className="z-10" onClick={() => {
				column.toggleSorting(column.getIsSorted() === "asc")
				}}>
				Title
				<ArrowUpDown className="ml-2 h-4, w-4"/>
			</Button>	
		},
		cell: ({ row }) => {
			const title = row.getValue("title")
			const url = row.getValue("gm_url")
			// console.log(row.gm_url)
	
			return <a className="text-left font-medium" href={`${url}`} target="_blank">{`${title}`}</a>
		},
	},
	{
		accessorKey: "gm_url",
		cell: null,
		header: null
	},
	{
		accessorKey: "id",
		cell: null,
		header: null
	},
	{
		accessorKey: "rating",
		header: "Rating",
	},
	{
		accessorKey: "category",
		header: "Category",
		filterFn: categoryFilterFn,
	},
	{
		accessorKey: "status",
		header: "Status",
		cell: ({row}) => {
			const status = row.getValue("status")
			const StatusIcon = status_icon[`${status}`]
			return <div className="flex justify-center items-center gap-2">
				<StatusIcon></StatusIcon>
				<p>{capitalizeFirstLetter(status)}</p>
			</div>
		},
		filterFn: categoryFilterFn,
	},
	{
		accessorKey: "website",
		header: "Website",
		cell: ({ row }) => {
			const url = row.getValue("website")
	
			return <a className="text-left font-medium" href={`${url}`} target="_blank">{`${url}`}</a>
		},
	},
	{
		accessorKey: "phone",
		header: "Phone",
		cell: ({ row }) => {
			const phone = row.getValue("phone")
	
			return <a className="text-left font-medium" href={`tel:${phone}`} target="_blank">{`${phone}`}</a>
		},
	},
	{
		id: "actions",
		cell: ({ row }) => {
			const title = row.getValue('title')
			const category = row.getValue('category')
			const website = row.getValue('website')
			const phone = row.getValue('phone')
			const status = row.getValue('status')
			const id = row.getValue('id')
			const [isDialogOpen, setIsDialogOpen] = useState(false)

			const statuses = [
				{
					value: "idle",
					label: "Idle",
					icon: CircleIcon,
				},
				{
					value: "in progress",
					label: "In Progress",
					icon: StopwatchIcon,
				},
				{
					value: "done",
					label: "Done",
					icon: CheckCircledIcon,
				},
				{
					value: "canceled",
					label: "Canceled",
					icon: CrossCircledIcon,
				},
			]
			function ComboBoxResponsive({selectedStatus, setSelectedStatus}) {
				const [open, setOpen] = useState(false)
				const isDesktop = useMediaQuery({ query: "(min-width: 768px)"})

			   
				if (isDesktop) {
				  return (
					<Popover open={open} onOpenChange={setOpen}>
					  <PopoverTrigger asChild>
						<Button variant="outline" className="w-[150px] justify-start">
						  {selectedStatus ? <div className="flex gap-2 items-center"><selectedStatus.icon></selectedStatus.icon>{selectedStatus.label}</div> : <>+ Set status</>}
						</Button>
					  </PopoverTrigger>
					  <PopoverContent className="w-[200px] p-0" align="start">
						<StatusList setOpen={setOpen} setSelectedStatus={setSelectedStatus} />
					  </PopoverContent>
					</Popover>
				  )
				}
			   
				return (
				  <Drawer open={open} onOpenChange={setOpen}>
					<DrawerTrigger asChild>
					  <Button variant="outline" className="w-[150px] justify-start">
						{selectedStatus ? <>{selectedStatus.label}</> : <>+ Set status</>}
					  </Button>
					</DrawerTrigger>
					<DrawerContent>
					  <div className="mt-4 border-t">
						<StatusList setOpen={setOpen} setSelectedStatus={setSelectedStatus} />
					  </div>
					</DrawerContent>
				  </Drawer>
				)
			  }
			   
			  function StatusList({
				setOpen,
				setSelectedStatus,
			  }: {
				setOpen: (open: boolean) => void
				setSelectedStatus: (status) => void
			  }) {
				return (
				  <Command>
					{/* <CommandInput placeholder="Filter status..." /> */}
					<CommandList>
					  <CommandEmpty>No results found.</CommandEmpty>
					  <CommandGroup>
						{statuses.map((status) => (
						  <CommandItem
							key={status.value}
							value={status.value}
							onSelect={(value) => {
							  setSelectedStatus(
								statuses.find((priority) => priority.value === value) || null
							  )
							  setOpen(false)
							}}
							className="flex gap-2"
						  >
							<status.icon></status.icon>
							{status.label}
						  </CommandItem>
						))}
					  </CommandGroup>
					</CommandList>
				  </Command>
				)
			  }
			const [selectedStatus, setSelectedStatus] = useState({
				value: status,
				label: capitalizeFirstLetter(status),
				icon: status_icon[status]
			})

			let titleRef = useRef(null)
			let categoryRef = useRef(null)
			let websiteRef = useRef(null)
			let phoneRef = useRef(null)
		
			return <>
				<DropdownMenu>
					<DropdownMenuTrigger asChild>
					<Button variant="ghost" className="h-8 w-8 p-0">
						<span className="sr-only">Open menu</span>
						<MoreHorizontal className="h-4 w-4" />
					</Button>
					</DropdownMenuTrigger>
					<DropdownMenuContent align="end">
					<DropdownMenuLabel>Actions</DropdownMenuLabel>
					<DropdownMenuItem onClick={() => {setIsDialogOpen(true)}}>
						Edit entry
					</DropdownMenuItem>
					</DropdownMenuContent>
				</DropdownMenu>
				<Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
					<DialogContent>
						<DialogHeader>
							<DialogTitle>Edit entry</DialogTitle>
							<DialogDescription>
								Make changes to this entru. Click save when you`re done.
							</DialogDescription>
						</DialogHeader>
							<div className="grid gap-4 py-4">
								<div className="grid grid-cols-4 items-center gap-4">
									<Label htmlFor="name" className="text-right">
										Title
									</Label>
									<Input ref={titleRef} id="title" defaultValue={title} className="col-span-3"/>
								</div>
								<div className="grid grid-cols-4 items-center gap-4">
									<Label htmlFor="username" className="text-right">
										Category
									</Label>
									<Input ref={categoryRef} id="category" defaultValue={category} className="col-span-3"/>
								</div>
								<div className="grid grid-cols-4 items-center gap-4">
									<Label htmlFor="name" className="text-right">
										Website
									</Label>
									<Input ref={websiteRef} id="website" defaultValue={website} className="col-span-3"/>
								</div>
								<div className="grid grid-cols-4 items-center gap-4">
									<Label htmlFor="name" className="text-right">
										Phone
									</Label>
									<Input ref={phoneRef} id="phone" defaultValue={phone} className="col-span-3"/>
								</div>
								<div className="grid grid-cols-4 items-center gap-4">
									<Label htmlFor="name" className="text-right">
										Status
									</Label>
									<ComboBoxResponsive selectedStatus={selectedStatus}
									 setSelectedStatus={setSelectedStatus}></ComboBoxResponsive>
								</div>
							</div>
							<DialogFooter>
								<Button type="submit" onClick={() => {
									const updated_lead = {
										title : titleRef.current.value,
										category : categoryRef.current.value,
										website : websiteRef.current.value,
										phone : phoneRef.current.value,
										status : selectedStatus.value
									}
									fetch(encodeURI(`http://localhost:5000/leads/${id}`), {
										method: "PUT",
										headers: { 
											'Content-type': 'application/json'
										}, 
										body: JSON.stringify(updated_lead)
									}).then((data) => {console.log(data)}).then(() => location.reload())
								}}>Save changes</Button>
							</DialogFooter>
					</DialogContent>
				</Dialog>
			</>
		},
	},
]
