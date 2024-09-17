"use client"

import { Button } from "@/components/ui/button"
import { ColumnDef } from "@tanstack/react-table"
import { stat } from "fs"
import { ArrowUpDown } from "lucide-react"

import {
	CheckCircledIcon,
	CircleIcon,
	CrossCircledIcon,
	StopwatchIcon,
  } from "@radix-ui/react-icons"
import capitalizeFirstLetter from "../capitalize"

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
		case 'cancled':
			return CrossCircledIcon
		default:
			return -1
	}
}

const status_icon = {
	"idle": CircleIcon,
	"in progress": StopwatchIcon,
	"done": CheckCircledIcon,
	"cancled": CrossCircledIcon
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
]
