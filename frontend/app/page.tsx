import capitalizeFirstLetter from "./capitalize"
import { Payment, columns } from "./components/columns"
import { DataTable } from "./components/data-table"


async function getData(): Promise<Payment[]> {
	const data = await fetch("http://127.0.0.1:5000/leads", {cache: "no-store"})
	const leads = (await data.json()).map((lead) => {
		return {
			id : lead.id,
			title: lead.title,
			rating: lead.rating && `${lead.rating.stars} ( ${lead.rating.amount} )`,
			gm_url: lead.gm_url,
			category: lead.category,
			website: lead.website,
			phone: lead.phone,
			status: lead.status,
		}
	})
	return leads
  }

export default async function Home() {
	const data = await getData()
	let unique_categories = Array.from(new Set(data.map((lead) => lead.category)))
	let categories = unique_categories.map((category) => {
		return {
			value: category,
			label: capitalizeFirstLetter(category)
		}
	})
	

	return (
		<div className="min-h-screen bg-background shadow-[inset_0_-2px_0_rgba(20,20,20,1)]">
			<main className="h-full w-full flex justify-center">
				<div className="max-w-[1280px]">
					<DataTable columns={columns} data={data} categories={categories}></DataTable>
				</div>
			</main>
		</div>
  	);
}
